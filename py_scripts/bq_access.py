import os
from google.cloud.exceptions import NotFound
from google.cloud import bigquery


def table_exists(big_query_client, table_id):
    try:
        big_query_client.get_table(table_id)
        return True
    except NotFound:
        return False


def database_exists(big_query_client, dataset_name):
    try:
        big_query_client.get_dataset(dataset_name)
        return True
    except NotFound:
        return False


def dataset_create(big_query_client, dataset_name, location):
    if database_exists(big_query_client, dataset_name):
        raise ValueError(f"Database {dataset_name} already exists.")
    dataset_id = big_query_client.dataset(dataset_name)
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = location
    big_query_client.create_dataset(dataset)
    print(f"Created dataset {dataset_name} in {location}.")


def load_blob(big_query_client, job_config, blob_uri, warehouse_name, blob_name, location):
    warehouse_id = os.getenv("GOOGLE_CLOUD_PROJECT") + '.' + warehouse_name + "_raw"
    destination_table_id = warehouse_id + '.' + blob_name

    if not database_exists(big_query_client, warehouse_name):
        dataset_create(big_query_client, warehouse_name, location)

    if not database_exists(big_query_client, warehouse_name + "_raw"):
        dataset_create(big_query_client, warehouse_name + "_raw", location)

    load_job = big_query_client.load_table_from_uri(
        blob_uri,
        destination_table_id,
        location=location,
        job_config=job_config,
    )
    load_job.result()

    print(f"Loaded {load_job.output_rows} rows into {destination_table_id}.")


def load_blob_as_ext(big_query_client, external_config, blob_uri, warehouse_name, blob_name, location):
    warehouse_id = os.getenv("GOOGLE_CLOUD_PROJECT") + '.' + warehouse_name + "_raw"
    destination_table_id = warehouse_id + '.' + blob_name

    if not database_exists(big_query_client, warehouse_name):
        dataset_create(big_query_client, warehouse_name, location)

    if not database_exists(big_query_client, warehouse_name + "_raw"):
        dataset_create(big_query_client, warehouse_name + "_raw", location)

    create_external_table(big_query_client, external_config, destination_table_id, blob_uri)


def create_external_table(big_query_client, external_config, destination_table_id, blob_uri):
    external_config.source_uris = [blob_uri]

    table = bigquery.Table(destination_table_id)
    table.external_data_configuration = external_config

    big_query_client.create_table(table, exists_ok=True)
    print(f"External table {destination_table_id} referencing {blob_uri} was created.")
