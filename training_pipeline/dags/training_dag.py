import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

from utils import *

class AppConst:
    DOCKER_USER = Variable.get("DOCKER_USER", "mlopsvn")


class AppPath:
    MLOPS_CRASH_COURSE_CODE_DIR = Path(Variable.get("MLOPS_CRASH_COURSE_CODE_DIR"))
    TRAINING_PIPELINE_DIR = MLOPS_CRASH_COURSE_CODE_DIR / "training_pipeline"
    FEATURE_REPO = TRAINING_PIPELINE_DIR / "feature_repo"
    ARTIFACTS = TRAINING_PIPELINE_DIR / "artifacts"

with DAG(
    dag_id="training_pipeline",
    default_args=DefaultConfig.DEFAULT_DAG_ARGS,
    schedule_interval="@once",
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=["training_pipeline"],
) as dag:
    data_extraction_task = DockerOperator(
        image="driver-recommendation/training_pipeline:0.0",
        task_id="data_extraction_task",
        command="bash -c 'cd src && python data_extraction.py'",
        mounts=[
            Mount(
                source=AppPath.ARTIFACTS.absolute().as_posix(),
                target="/training_pipeline/artifacts",
                type="bind",
            )
        ],
        network_mode="host",
        **DefaultConfig.DEFAULT_DOCKER_OPERATOR_ARGS,
    )
    data_validation_task = DockerOperator(
        image="driver-recommendation/training_pipeline:0.0",
        task_id="data_validation_task",
        command="bash -c 'cd src && python data_validation.py'",
        network_mode="host",
        mounts=[
            Mount(
                source=AppPath.ARTIFACTS.absolute().as_posix(),
                target="/training_pipeline/artifacts",
                type="bind",
            )
        ],
        **DefaultConfig.DEFAULT_DOCKER_OPERATOR_ARGS,
    )
    data_preparation_task = DockerOperator(
        image="driver-recommendation/training_pipeline:0.0",
        task_id="data_preparation_task",
        command="bash -c 'cd src && python data_preparation.py'",
        network_mode="host",
        mounts=[
            Mount(
                source=AppPath.ARTIFACTS.absolute().as_posix(),
                target="/training_pipeline/artifacts",
                type="bind",
            )
        ],
        **DefaultConfig.DEFAULT_DOCKER_OPERATOR_ARGS,
    )
    model_training_task = DockerOperator(
        image="driver-recommendation/training_pipeline:0.0",
        task_id="model_training_task",
        command="bash -c 'cd src && python model_training.py'",
        network_mode="host",
        mounts=[
            Mount(
                source=AppPath.ARTIFACTS.absolute().as_posix(),
                target="/training_pipeline/artifacts",
                type="bind",
            )
        ],
        **DefaultConfig.DEFAULT_DOCKER_OPERATOR_ARGS,
    )
    model_evaluation_task = DockerOperator(
        image="driver-recommendation/training_pipeline:0.0",
        task_id="model_evaluation_task",
        command="bash -c 'cd src && python model_evaluation.py'",
        network_mode="host",
        mounts=[
            Mount(
                source=AppPath.ARTIFACTS.absolute().as_posix(),
                target="/training_pipeline/artifacts",
                type="bind",
            )
        ],
        **DefaultConfig.DEFAULT_DOCKER_OPERATOR_ARGS,
    )
    model_validation_task = DockerOperator(
        image="driver-recommendation/training_pipeline:0.0",
        task_id="model_validation_task",
        command="bash -c 'cd src && python model_validation.py'",
        network_mode="host",
        mounts=[
            Mount(
                source=AppPath.ARTIFACTS.absolute().as_posix(),
                target="/training_pipeline/artifacts",
                type="bind",
            )
        ],
        **DefaultConfig.DEFAULT_DOCKER_OPERATOR_ARGS,
    )

    (
        data_extraction_task
        >> data_validation_task
        >> data_preparation_task
        >> model_training_task
        >> model_evaluation_task
        >> model_validation_task
    )