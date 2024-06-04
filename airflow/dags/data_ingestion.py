import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage

import pyarrow.csv as pv
import pyarrow.parquet as pq
import pandas as pd

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
NYT_KEY = os.environ.get("NYT_KEY")
BUCKET = os.environ.get("GCP_GCS_BUCKET")

dataset_file = "new_york_times_most_viewed.json"
dataset_url = (
    f"https://api.nytimes.com/svc/mostpopular/v2/viewed/1.json?api-key={NYT_KEY}"
)
path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "trips_data_all")


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    generation_match_precondition = 0

    blob.upload_from_filename(
        source_file_name, if_generation_match=generation_match_precondition
    )

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")


["title", "abstract", "adx_keywords", "des_facet", "media"]


def transform_dataset():
    df = pd.read_json("/opt/airflow/new_york_times_most_viewed.json")
    df = df["results"]
    filtered_data = []

    for item in df:
        filtered_item = {
            key: item[key]
            for key in ["title", "abstract", "des_facet", "media"]
            if key in item
        }
        filtered_data.append(filtered_item)

    filtered_df = pd.DataFrame(filtered_data)

    filtered_df.to_json(
        "/opt/airflow/transformed_data.json", orient="records", lines=True
    )


default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="data_ingestion_gcs_dag",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=["paris-velib"],
) as dag:

    download_dataset_task = BashOperator(
        task_id="download_dataset_task",
        bash_command=f"curl -sSL {dataset_url} > {path_to_local_home}/{dataset_file}",
    )

    transform_dataset_task = PythonOperator(
        task_id="transform_dataset_task", python_callable=transform_dataset
    )

    download_dataset_task >> transform_dataset_task

"""
    upload_to_gcs_task = PythonOperator(
        task_id="upload_to_gcs_task",
        python_callable=upload_blob,
        op_kwargs={
            "bucket_name": BUCKET,
            "source_file_name": "/opt/airflow/new_york_times_most_viewed.csv",
            "destination_blob_name": "new_york_times_most_viewed.csv",
        },
    )
"""
