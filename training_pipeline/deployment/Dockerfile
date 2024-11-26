FROM python:3.9-slim AS build

RUN apt-get update

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY deployment/requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.9-slim

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . /training_pipeline
WORKDIR /training_pipeline

ENV TRAINING_PIPELINE_DIR='/training_pipeline/'
ENV MLFLOW_TRACKING_URI="http://localhost:5000"

ENV RANDOM_SEED="17"
ENV TEST_SIZE="0.2"
ENV TARGET_COL="trip_completed"
 
ENV EXPERIMENT_NAME="elastic-net"
ENV ALPHA="0.5"
ENV L1_RATIO="0.1"
ENV MLFLOW_TRACKING_URI="http://localhost:5000"
 
ENV RMSE_THRESHOLD="0.2"
ENV MAE_THRESHOLD="0.2"
ENV REGISTERED_MODEL_NAME="sklearn-elastic-net-reg"