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
    request_body.convert_datetimes()  # Convert all datetime strings to datetime objects

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
    p = Pickler()
    response = p.flatten(training_df)
    Log().log.info(f"response from datasource store: ", {str(response)})
    return response

@app.post("/get-online-features")
def post_online_store(request_body: OnlineRequestBody):
    store = FeatureStore(repo_path=AppPath.FEATURE_REPO)
    print(request_body.driverIds)
    features = store.get_online_features(
        features=["driver_stats:acc_rate", "driver_stats:conv_rate", "driver_stats:avg_daily_trips"],
        entity_rows=[{"driver_id": driver_id} for driver_id in request_body.driverIds],
    ).to_df()
    p = Pickler()
    response = p.flatten(features)
    Log().log.info(f"response from online store: ", {str(response)})
    return response
