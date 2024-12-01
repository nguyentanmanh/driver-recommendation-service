from typing import List, Union
import jsonpickle.ext.pandas as jsonpickle_pandas
from jsonpickle.pickler import Pickler
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from feast import FeatureStore
from datetime import datetime

from pathlib import Path
import os
import sys
import logging
import base64
import pickle

class AppConst:
    LOG_LEVEL = logging.DEBUG

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

jsonpickle_pandas.register_handlers()

app = FastAPI()

class AppPath:
    ROOT = Path(os.environ.get("DATA_PIPELINE_DIR", "/data_pipeline"))
    DATA = ROOT / "data"
    DATA_SOURCES = ROOT / "data_sources"
    FEATURE_REPO = ROOT / "feature_repo"

class OfflineRequestBody(BaseModel):
    driverIds: List[int]
    datetimes: List[Union[str, datetime]]

    def convert_datetimes(self):
        self.datetimes = [datetime.fromisoformat(dt) if isinstance(dt, str) else dt for dt in self.datetimes]

class OnlineRequestBody(BaseModel):
    driverIds: List[int]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/get-offline-features")
def post_offline_store(request_body: OfflineRequestBody):
    request_body.convert_datetimes()

    store = FeatureStore(repo_path=AppPath.FEATURE_REPO)
    entity_df = pd.DataFrame.from_dict(
        {
            "driver_id": request_body.driverIds,
            "datetime": request_body.datetimes,
        }
    )
    training_df = store.get_historical_features(
        entity_df=entity_df,
        features=["driver_stats:acc_rate", "driver_stats:conv_rate", "driver_stats:avg_daily_trips"],
    ).to_df()

    # Encode DataFrame into JSON-compatible format
    response = {
        "values": base64.b64encode(pickle.dumps(training_df)).decode("utf-8"),
        "index": training_df.index.tolist(),  # Explicitly provide index
        "columns": training_df.columns.tolist(),  # Explicitly provide columns
    }

    Log().log.info(f"response from datasource store: {response}")
    return response

@app.post("/get-online-features")
def post_online_store(request_body: OnlineRequestBody):
    """
    Fetches online features from the Feature Store for the provided driver IDs.
    Serializes the response in a JSON-compatible format with Base64 encoding.
    """
    try:
        # Initialize the feature store
        store = FeatureStore(repo_path=AppPath.FEATURE_REPO)

        # Prepare entity rows from request
        entity_rows = [{"driver_id": driver_id} for driver_id in request_body.driverIds]

        # Fetch online features as a DataFrame
        features_df = store.get_online_features(
            features=["driver_stats:acc_rate", "driver_stats:conv_rate", "driver_stats:avg_daily_trips"],
            entity_rows=entity_rows,
        ).to_df()

        # Serialize the DataFrame
        response = {
            "values": base64.b64encode(pickle.dumps(features_df)).decode("utf-8"),
            "index": features_df.index.tolist(),  # Explicitly include index
            "columns": features_df.columns.tolist(),  # Explicitly include columns
        }

        # Log the response
        Log().log.info(f"Response from online store: {response}")

        # Return the response
        return response
    except Exception as e:
        # Log the error
        Log().log.error(f"Error in fetching online features: {e}")
        return {"error": str(e)}, 500
