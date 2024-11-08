import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.bash import BashOperator
from utils import *

import pendulum

def _training_model():
  return randint(1, 10) # return an integer between 1 - 10

with DAG(
    dag_id="my_dag_4",
    default_args=DefaultConfig.DEFAULT_DAG_ARGS,
    schedule_interval="@once",
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=["data_pipeline"],
) as dag:
    # Tasks are implemented under the dag object
    training_model_A = PythonOperator(
      task_id="training_model_A",
      python_callable=_training_model
    )

    training_model_B = PythonOperator(
      task_id="training_model_B",
      python_callable=_training_model
    )

    training_model_C = PythonOperator(
      task_id="training_model_C",
      python_callable=_training_model
    )
