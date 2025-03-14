from google.cloud import bigquery, storage
from gcp_setup import *
from gcs_access import *
from bq_access import *
from dbt_configuration import *


"""
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

def load_environment_variables(dotenv_path):
    if not load_dotenv(dotenv_path):
        raise FileNotFoundError("File .env was not found or the file is empty.")

env_path = find_dotenv()
load_environment_variables(env_path)

project_directory = str(Path.cwd().parent)
dbt_scripts_directory = project_directory + "/" + "dbt_scripts"
dbt_models_directory = dbt_scripts_directory + "/" + "models"
dbt_macros_directory = dbt_scripts_directory + "/" + "macros"
"""

set_google_credentials()

dbt_scripts_directory = "/opt/dbt_scripts"
dbt_models_directory = "/opt/dbt_scripts/models"
dbt_macros_directory = "/opt/dbt_scripts/macros"

big_query_client = bigquery.Client()
google_cloud_client = storage.Client()

source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON

external_config = bigquery.ExternalConfig(source_format)
external_config.autodetect = True


"""
job_config = bigquery.LoadJobConfig(
    autodetect=True,
    source_format=source_format,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
)

for blob_name, blob_uri in blob_uri_generator(google_cloud_client, os.getenv("BUCKET_NAME")):
    table_names.append(blob_name)
    load_blob(big_query_client=big_query_client,
              job_config=job_config,
              blob_uri=blob_uri,
              warehouse_name=os.getenv("WAREHOUSE_NAME"),
              blob_name=blob_name,
              location=os.environ["LOCATION"])
"""

table_names = []
for blob_name, blob_uri in blob_uri_generator(google_cloud_client, os.getenv("BUCKET_NAME")):
    table_names.append(blob_name)
    load_blob_as_ext(big_query_client=big_query_client,
                     external_config=external_config,
                     blob_uri=blob_uri,
                     warehouse_name=os.getenv("WAREHOUSE_NAME"),
                     blob_name=blob_name,
                     location=os.environ["LOCATION"])

schema_yaml = get_schema_yaml(table_names)
create_yaml(schema_yaml, dbt_models_directory, "schema")

metadata_sql_macros = get_metadata_sql_macros(table_names)
create_sql_macros(metadata_sql_macros, dbt_macros_directory, "metadata")
