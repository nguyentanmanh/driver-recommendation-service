import pandas as pd

from datetime import datetime
import requests
import pickle
import base64

import jsonpickle.ext.pandas as jsonpickle_pandas
from jsonpickle.unpickler import Unpickler

from utils import *

Log(AppConst.DATA_EXTRACTION)
AppPath()

# Register pandas handlers with jsonpickle
jsonpickle_pandas.register_handlers()

def extract_data():
    Log().log.info("Start extract_data")
    inspect_curr_dir()
    config = Config()
    Log().log.info(f"config: {config.__dict__}")

    # Load driver order data
    batch_input_file = AppPath.ROOT / config.batch_input_file
    inspect_dir(batch_input_file)
    orders = pd.read_csv(batch_input_file, sep="\t")
    orders["datetime"] = pd.to_datetime(orders["event_timestamp"])
    orders = orders.drop(["event_timestamp"], axis=1)

    driver_list = orders["driver_id"].values.tolist()
    date_time_list = [str(datetime.utcfromtimestamp(dt.astype(int) / 1e9).isoformat()) for dt in orders["datetime"].values] 

    # call api
    url = 'http://localhost:8000/get-offline-features'

    payload = {
        "driverIds": driver_list,
        "datetimes": date_time_list
    }


    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        try:
            print("Response from server:")
            response_json = response.json()
    
            # Decode Base64 string and unpickle the DataFrame
            serialized_data = response_json.get("values")
            if not serialized_data:
                raise ValueError("Missing 'values' in server response.")
    
            df = pickle.loads(base64.b64decode(serialized_data))
    
            # Ensure 'index' and 'columns' are applied (in case of unexpected reconstruction issues)
            df.index = response_json.get("index", df.index)
            df.columns = response_json.get("columns", df.columns)
    
            # Merge the features with the orders DataFrame
            merged_df = pd.merge(orders, df, on=["driver_id", "datetime"])
    
            # Drop unnecessary columns after merging
            merged_df = merged_df.drop(["driver_id", "datetime"], axis=1)
    
            # Log schema and example features
            Log().log.info("----- Feature schema -----")
            Log().log.info(merged_df.info())
            Log().log.info("----- Example features -----")
            Log().log.info(merged_df.head())
    
            # Write merged features to a Parquet file
            to_parquet(merged_df, AppPath.TRAINING_PQ)
            inspect_dir(AppPath.TRAINING_PQ.parent)

        except Exception as e:
            # Handle any errors in processing
            Log().log.error(f"Error processing server response: {e}")
            print(f"Error processing server response: {e}")
    else:
        # Handle unsuccessful HTTP responses
        print(f"Failed to get response. Status code: {response.status_code}")
        print("Response content:", response.content)

if __name__ == "__main__":
    extract_data()