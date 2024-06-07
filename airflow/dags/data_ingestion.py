import os
from datetime import datetime
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from google.cloud import storage
import pyarrow.csv as pv
import pyarrow.parquet as pq
import pandas as pd
from transform import transform_dataset
from load_to_bigquery import load_data_to_bq

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
NYT_KEY = os.environ.get("NYT_KEY")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
now = datetime.now()
date_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")

dataset_file = f"new_york_times_most_viewed_{date_time_str}.json"

dataset_url = (
    f"https://api.nytimes.com/svc/mostpopular/v2/viewed/1.json?api-key={NYT_KEY}"
)
path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "trips_data_all")


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
    list_all_files = os.listdir(path_to_local_home)
    latest_file = max(list_all_files, key=os.path.getctime)

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(latest_file)
    generation_match_precondition = 0

    blob.upload_from_filename(
        latest_file, if_generation_match=generation_match_precondition
    )

    print(f"File {latest_file} uploaded to {latest_file}.")


default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

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
        do_xcom_push=True,
    )

    transform_dataset_task = PythonOperator(
        task_id="transform_dataset_task",
        python_callable=transform_dataset,
    )

    upload_to_gcs_task = PythonOperator(
        task_id="upload_to_gcs_task",
        python_callable=upload_blob,
        op_kwargs={
            "bucket_name": BUCKET,
            "source_file_name": f"/opt/airflow/{dataset_file}",
            "destination_blob_name": f"{dataset_file}",
        },
    )

    load_data_to_bigquery_task = PythonOperator(
        task_id="load_data_to_bq_task",
        python_callable=load_data_to_bq,
        op_kwargs={
            "uri": "gs://nyt_most_viewved_bucket/",
            "table_id": "parisvelib.ny_most_viewed.nyt_most_viewed_articles",
        },
    )

    (
        download_dataset_task
        >> transform_dataset_task
        >> upload_to_gcs_task
        >> load_data_to_bigquery_task
    )
