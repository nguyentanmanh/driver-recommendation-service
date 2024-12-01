FROM python:3.9-buster AS build

RUN apt-get update

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip

COPY deployment/requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.9-buster

COPY --from=build /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV MLFLOW_TRACKING_URI="http://localhost:5000"
# ENV MLFLOW_TRACKING_URI="http://mlflow:5000"
ENV BATCH_INPUT_FILE="./data/batch_request.csv"
ENV REGISTERED_MODEL_FILE="./artifacts/registered_model_version.json"
ENV MONITORING_SERVICE_API="http://monitoring:8309/iterate"

COPY . /model_serving
WORKDIR /model_serving