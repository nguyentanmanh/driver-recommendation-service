import logging
from pathlib import Path
import json
import os
import sys

class AppConst:
    LOG_LEVEL = logging.DEBUG
    BENTOML_MODEL_SAVING = "bentoml_model_saving"
    BENTOML_SERVICE = "bentoml_service"
    DATA_EXTRACTION = "data_extraction"
    BATCH_PREDICTION = "batch_prediction"

# the encoder helps to convert NumPy types in source data to JSON-compatible types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.void):
            return None

        if isinstance(obj, (np.generic, np.bool_)):
            return obj.item()

        if isinstance(obj, np.ndarray):
            return obj.tolist()

        return obj

class AppPath:
    # set MODEL_SERVING_DIR in dev environment for quickly testing the code
    ROOT = Path(os.environ.get("MODEL_SERVING_DIR", "/model_serving"))
    DATA = ROOT / "data"
    DATA_SOURCES = ROOT / "data_sources"
    FEATURE_REPO = ROOT / "feature_repo"
    ARTIFACTS = ROOT / "artifacts"

    BATCH_INPUT_PQ = ARTIFACTS / "batch_input.parquet"
    BATCH_OUTPUT_PQ = ARTIFACTS / "batch_output.parquet"

    def __init__(self) -> None:
        AppPath.ARTIFACTS.mkdir(parents=True, exist_ok=True)

class Config:
    def __init__(self) -> None:
        import numpy as np

        self.feature_dict = {
            "conv_rate": np.float64,
            "acc_rate": np.float64,
            "avg_daily_trips": np.int64,
            "trip_completed": np.int64,
        }
        self.mlflow_tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
        self.batch_input_file = os.environ.get("BATCH_INPUT_FILE")
        self.registered_model_file = os.environ.get("REGISTERED_MODEL_FILE")
        self.monitoring_service_api = os.environ.get("MONITORING_SERVICE_API")


class Log:
    log: logging.Logger = None

    def __init__(self, name="") -> None:
        if Log.log == None:
            Log.log = self._init_logger(name)

    def _init_logger(self, name):
        logger = logging.getLogger(name)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        logger.setLevel(AppConst.LOG_LEVEL)
        return logger

def load_json(path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

from typing import Optional, Dict, Any, List

import bentoml
import pandas as pd
import numpy as np
import mlflow
import requests
import jsonpickle.ext.pandas as jsonpickle_pandas

from jsonpickle.unpickler import Unpickler
from pydantic import BaseModel
from bentoml.io import JSON
from mlflow.models.signature import ModelSignature

# Register pandas handlers with jsonpickle
jsonpickle_pandas.register_handlers()

Log(AppConst.BENTOML_SERVICE)
AppPath()
pd.set_option("display.max_columns", None)
config = Config()
Log().log.info(f"config: {config.__dict__}")

def save_model() -> bentoml.Model:
    Log().log.info("start save_model")
    
    registered_model_file = AppPath.ROOT / config.registered_model_file
    Log().log.info(f"registered_model_file: {registered_model_file}")
    registered_model_dict = load_json(registered_model_file)
    Log().log.info(f"registered_model_dict: {registered_model_dict}")

    run_id = registered_model_dict["_run_id"]
    model_name = registered_model_dict["_name"]
    model_version = registered_model_dict["_version"]
    model_uri = registered_model_dict["_source"]

    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    mlflow_model = mlflow.pyfunc.load_model(model_uri=model_uri)
    Log().log.info(mlflow_model.__dict__)
    model = mlflow.sklearn.load_model(model_uri=model_uri)
    model_signature: ModelSignature = mlflow_model.metadata.signature

    # construct feature list
    feature_list = []
    for name in model_signature.inputs.input_names():
        feature_list.append(name)

    # save model using bentoml
    bentoml_model = bentoml.sklearn.save_model(
        model_name,
        model,
        # model signatures for runner inference
        signatures={
            "predict": {
                "batchable": False,
            },
        },
        labels={
            "owner": "mlopsvn",
        },
        metadata={
            "mlflow_run_id": run_id,
            "mlflow_model_name": model_name,
            "mlflow_model_version": model_version,
        },
        custom_objects={
            "feature_list": feature_list,
        },
    )
    Log().log.info(bentoml_model.__dict__)
    return bentoml_model

bentoml_model = save_model()
feature_list = bentoml_model.custom_objects["feature_list"]
bentoml_runner = bentoml.sklearn.get(bentoml_model.tag).to_runner()
svc = bentoml.Service(bentoml_model.tag.name, runners=[bentoml_runner])

def predict(request: np.ndarray) -> np.ndarray:
    Log().log.info(f"start predict")
    result = bentoml_runner.predict.run(request)
    Log().log.info(f"result: {result}")
    return result

class InferenceRequest(BaseModel):
    request_id: str
    driver_ids: List[int]


class InferenceResponse(BaseModel):
    prediction: Optional[float]
    error: Optional[str]

@svc.api(
    input=JSON(pydantic_model=InferenceRequest),
    output=JSON(pydantic_model=InferenceResponse),
)
def inference(request: InferenceRequest, ctx: bentoml.Context) -> Dict[str, Any]:
    """
    Example request: {"request_id": "uuid-1", "driver_ids":[1001,1002,1003,1004,1005]}
    """
    Log().log.info(f"start inference")
    response = InferenceResponse()
    try:
        Log().log.info(f"request: {request}")
        driver_ids = request.driver_ids
        
        # Define the URL of the FastAPI endpoint
        url = 'http://feastapp:8000/get-online-features'
        
        # Define the request payload
        payload = {"driverIds": [driver_id for driver_id in driver_ids]} 

        # Define the headers
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        Log().log.info(f"call API request online store data: {payload}")
        # Make the POST request
        response_from_feature_app = requests.post(url, json=payload, headers=headers)
        
        # Check if the request was successful
        if response_from_feature_app.status_code == 200:
            response_json = response_from_feature_app.json()
            # Use Unpickler to parse the response to a DataFrame
            u = Unpickler()
            df = u.restore(response_json)
            Log().log.info(f"response from feature service: {df}")
        else:
            Log().log.error(f"Failed to get response from feature server. Status code: {response_from_feature_app.status_code}")
            Log().log.error(f"Error :", {response_from_feature_app.content})
            response.error = str(response_from_feature_app.content)
            ctx.response.status_code = 500
            return

        Log().log.info(f"online features: {df}")

        input_features = df.drop(["driver_id"], axis=1)
        input_features = input_features[feature_list]
        Log().log.info(f"input_features: {input_features}")

        result = predict(input_features)
        df["prediction"] = result
        best_idx = df["prediction"].argmax()
        best_driver_id = df["driver_id"].iloc[best_idx]
        Log().log.info(f"best_driver_id: {best_driver_id}")
        Log().log.info(f"df: {df}")

        response.prediction = best_driver_id
        ctx.response.status_code = 200

        # monitor
        monitor_df = df.iloc[[best_idx]]
        monitor_df = monitor_df.assign(request_id=[request.request_id])
        monitor_df = monitor_df.assign(best_driver_id=[best_driver_id])
        Log().log.info(f"monitor_df: {monitor_df}")
        monitor_request(monitor_df)

    except Exception as e:
        Log().log.error(f"error: {e}")
        response.error = str(e)
        ctx.response.status_code = 500

    Log().log.info(f"response: {response}")
    return response

def monitor_request(df: pd.DataFrame):
    Log().log.info("start monitor_request")
    try:
        data = json.dumps(df.to_dict(), cls=NumpyEncoder)

        Log().log.info(f"sending {data}")
        response = requests.post(
            config.monitoring_service_api,
            data=data,
            headers={"content-type": "application/json"},
        )

        if response.status_code == 200:
            Log().log.info(f"Success")
        else:
            Log().log.info(
                f"Got an error code {response.status_code} for the data chunk. Reason: {response.reason}, error text: {response.text}"
            )

    except requests.exceptions.ConnectionError as error:
        Log().log.error(
            f"Cannot reach monitoring service, error: {error}, data: {data}"
        )

    except Exception as error:
        Log().log.error(f"Error: {error}")