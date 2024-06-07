from google.cloud import bigquery
import os


def load_data_to_bq(uri, table_id):
    path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
    list_all_files = os.listdir(path_to_local_home)
    latest_file = max(list_all_files, key=os.path.getctime)
    uri = uri + latest_file

    client = bigquery.Client()

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)

    load_job.result()

    print(f"Loaded data from {uri} to {table_id}")
