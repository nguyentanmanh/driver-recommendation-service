import pandas as pandas

from datetime import datetime
import requests

import jsonpickle.ext.pandas as jsonpickle_pandas
from jsonpickle.unpickler import Unpickler
from utils import *

Log(AppConst.DATA_EXTRACTION)
AppPath()

# Register pandas handlers with jsonpickle
jsonpickle_pandas.register_handlers()

def extract_data():
    Log().log.info("start extract_data")
    inspect_curr_dir()

    # setup request
    inspect_dir(AppPath.DATA)
    orders = pd.read_csv(AppPath.DATA / "driver_orders.csv", sep="\t")
    orders["datetime"] = pd.to_datetime(orders["event_timestamp"])
    orders = orders.drop(["event_timestamp"], axis=1)

    driver_list = orders["driver_id"].values.tolist()
    date_time_list = [str(datetime.utcfromtimestamp(dt.astype(int) / 1e9).isoformat()) for dt in orders["datetime"].values] 

    # call api
    url = 'http://localhost:3000/get-offline-features'

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
        print("Response from server:")
        response_json = response.json()
        # Use Unpickler to parse the response to a DataFrame
        u = Unpickler()
        df = u.restore(response_json)

        merged_df = pd.merge(orders, df, on=['driver_id', 'datetime'])

        merged_df = merged_df.drop(["driver_id", "datetime"], axis=1)

        Log().log.info("----- Feature schema -----")
        Log().log.info(merged_df.info())

        Log().log.info("----- Example features -----")
        Log().log.info(merged_df.head())

        # Write to file
        to_parquet(merged_df, AppPath.TRAINING_PQ)
        inspect_dir(AppPath.TRAINING_PQ.parent)

    else:
        print(f"Failed to get response. Status code: {response.status_code}")
        print("Response content:", response.content)

    # call feature store service and get response


if __name__ == "__main__":
    extract_data()