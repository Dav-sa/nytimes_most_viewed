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
