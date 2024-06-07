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
from os import path


def transform_dataset():
    path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
    list_all_files = os.listdir(path_to_local_home)

    latest_file = max(list_all_files, key=os.path.getctime)

    df = pd.read_json(latest_file)
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
    filtered_df.to_json(f"/opt/airflow/{latest_file}", orient="records", lines=True)
