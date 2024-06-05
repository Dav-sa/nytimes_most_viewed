from google.cloud import bigquery


def load_data_to_bq(uri, table_id):

    client = bigquery.Client()

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)

    load_job.result()  # Waits for the job to complete.

    print(f"Loaded data from {uri} to {table_id}")
