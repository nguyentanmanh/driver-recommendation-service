import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import pendulum

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

from utils import *

with DAG(
    dag_id="stream_to_stores",
    default_args=DefaultConfig.DEFAULT_DAG_ARGS,
    schedule_interval="@once",
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=["data_pipeline"],
) as dag:
    stream_to_online_task = DockerOperator(
        image="driver-recommendation/data_pipeline:0.0",
        task_id="stream_to_online_task",
        network_mode="host",
        mounts=[
            Mount(
                source=AppPath.FEATURE_REPO.absolute().as_posix(),
                target="/data_pipeline/feature_repo",
                type="bind",
            ),
        ],
        command="/bin/bash -c 'cd src/stream_to_stores && python ingest.py --store online'",
        **DefaultConfig.DEFAULT_DOCKER_OPERATOR_ARGS,
    )

    stream_to_offline_task = DockerOperator(
        image="driver-recommendation/data_pipeline:0.0",
        task_id="stream_to_offline_task",
        network_mode="host",
        mounts=[
            Mount(
                source=AppPath.FEATURE_REPO.absolute().as_posix(),
                target="/data_pipeline/feature_repo",
                type="bind",
            ),
        ],
        **DefaultConfig.DEFAULT_DOCKER_OPERATOR_ARGS,
        command="/bin/bash -c 'cd src/stream_to_stores && python ingest.py --store offline'",
    )