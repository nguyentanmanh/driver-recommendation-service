import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from pathlib import Path

from airflow.models import Variable
from docker.types import Mount

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

from utils import *


class AppConst:
    DOCKER_USER = Variable.get("DOCKER_USER", "mlopsvn")


class AppPath:
    MLOPS_CRASH_COURSE_CODE_DIR = Path(Variable.get("MLOPS_CRASH_COURSE_CODE_DIR"))
    MODEL_SERVING_DIR = MLOPS_CRASH_COURSE_CODE_DIR / "model_serving"
    FEATURE_REPO = MODEL_SERVING_DIR / "feature_repo"
    ARTIFACTS = MODEL_SERVING_DIR / "artifacts"
    DATA = MODEL_SERVING_DIR / "data"

with DAG(
    dag_id="batch_serving_pipeline",
    default_args=DefaultConfig.DEFAULT_DAG_ARGS,
    schedule_interval="@once",
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=["model_serving"],
) as dag:
    data_extraction_task = DockerOperator(
        task_id="data_extraction_task",
        image="driver-recommendation/model_serving:0.0",
        command="bash -c 'cd src && python data_extraction.py'",
        mounts=[
            # artifacts
            Mount(
                source=AppPath.ARTIFACTS.absolute().as_posix(),
                target="/model_serving/artifacts",
                type="bind",
            ),
            # data
            Mount(
                source=AppPath.DATA.absolute().as_posix(),
                target="/model_serving/data",
                type="bind",
            ),
        ],
        network_mode="host",
        **DefaultConfig.DEFAULT_DOCKER_OPERATOR_ARGS,
    )

    batch_prediction_task = DockerOperator(
        task_id="batch_prediction_task",
        image="driver-recommendation/model_serving:0.0",
        mounts=[
            # artifacts
            Mount(
                source=AppPath.ARTIFACTS.absolute().as_posix(),
                target="/model_serving/artifacts",
                type="bind",
            ),
            # data
            Mount(
                source=AppPath.DATA.absolute().as_posix(),
                target="/model_serving/data",
                type="bind",
            ),
        ],
        network_mode="host",
        command="bash -c 'cd src && python batch_prediction.py'",
        **DefaultConfig.DEFAULT_DOCKER_OPERATOR_ARGS,
    )

    (data_extraction_task >> batch_prediction_task)
