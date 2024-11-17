#FROM apache/airflow:2.7.2
#FROM apache/airflow:slim-latest-python3.10
#FROM apache/airflow:latest-python3.10
FROM apache/airflow:2.10.3-python3.10

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gosu \
    && rm -rf /var/lib/apt/lists/*
USER airflow

# # Install psutil wheel for ARM64
# RUN pip install --no-cache-dir psutil --only-binary=:all:

COPY requirements-airflow.txt /requirements-airflow.txt
RUN pip install --no-cache-dir -r /requirements-airflow.txt