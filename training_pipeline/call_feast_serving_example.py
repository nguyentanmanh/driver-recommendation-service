import requests
import pandas as pd
import jsonpickle.ext.pandas as jsonpickle_pandas
from jsonpickle.unpickler import Unpickler
from datetime import datetime

# Register pandas handlers with jsonpickle
jsonpickle_pandas.register_handlers()

# Define the URL of the FastAPI endpoint
url = 'http://127.0.0.1:3000/get-offline-features'

# Define the request payload
payload = {
    "driverIds": [1001, 1002, 1003],
    "datetimes": [
        "2022-05-11T11:59:59",
        "2022-06-12T01:15:10",
        datetime.now().isoformat()
    ]
}

# Define the headers
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

# Make the POST request
response = requests.post(url, json=payload, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    print("Response from server:")
    response_json = response.json()
    # Use Unpickler to parse the response to a DataFrame
    u = Unpickler()
    df = u.restore(response_json)
    print(df)
else:
    print(f"Failed to get response. Status code: {response.status_code}")
    print("Response content:", response.content)

# Define the URL of the FastAPI endpoint
url = 'http://127.0.0.1:3000/get-offline-features'

orders = pd.read_csv("./data/driver_orders.csv", sep="\t")
orders["event_timestamp"] = pd.to_datetime(orders["event_timestamp"])

driver_list = orders["driver_id"].values.tolist()
date_time_list = [str(datetime.utcfromtimestamp(dt.astype(int) / 1e9).isoformat()) for dt in orders["event_timestamp"].values]

# Define the request payload
payload = {
    "driverIds": driver_list,
    "datetimes": date_time_list
}

# Define the headers
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

# Make the POST request
response = requests.post(url, json=payload, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    print("Response from server:")
    response_json = response.json()
    # Use Unpickler to parse the response to a DataFrame
    u = Unpickler()
    df = u.restore(response_json)
    print(df)
else:
    print(f"Failed to get response. Status code: {response.status_code}")
    print("Response content:", response.content)

# Define the URL of the FastAPI endpoint
url = 'http://127.0.0.1:3000/get-online-features'

# Define the request payload
payload = {
    "driverIds": [1001, 1002, 1003]
}

# Define the headers
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

# Make the POST request
response = requests.post(url, json=payload, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    print("Response from server:")
    response_json = response.json()
    # Use Unpickler to parse the response to a DataFrame
    u = Unpickler()
    df = u.restore(response_json)
    print(df)
else:
    print(f"Failed to get response. Status code: {response.status_code}")
    print("Response content:", response.content)
