FROM python:3.9-slim AS build

RUN apt-get update
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./deployment/requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.9-slim

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
    wget && \
  wget https://download.java.net/openjdk/jdk11/ri/openjdk-11+28_linux-x64_bin.tar.gz && \
  tar xvf openjdk-11+28_linux-x64_bin.tar.gz && \
  mv jdk-11*/ /opt/jdk11 && \
  apt-get autoremove -yqq --purge && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/opt/jdk11

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./ /data_pipeline
WORKDIR /data_pipeline

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]

EXPOSE 8000
