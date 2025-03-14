from gcp_setup import *
from gcs_access import *
from api_source_access import *
from google.cloud import storage
from dbt_configuration import *

"""
from dotenv import load_dotenv, find_dotenv

def load_environment_variables(dotenv_path):
    if not load_dotenv(dotenv_path):
        raise FileNotFoundError("File .env was not found or the file is empty.")

env_path = find_dotenv()
load_environment_variables(env_path)

project_directory = str(Path.cwd().parent)
dbt_scripts_directory = project_directory + "/" + "dbt_scripts"

profiles_yaml = get_profiles_yaml(4)
create_yaml(profiles_yaml, dbt_scripts_directory, "profiles")
"""

set_google_credentials()

google_cloud_client = storage.Client()

api_url, api_resources, _, api_leagues, api_endpoints = parse_api_config("/opt/config.yml")  # "../config.yml"
api_headers = get_api_headers()

if api_resources:
    for _, api_league, api_endpoint, endpoint_str in api_resource_endpoint_generator(api_resources, api_leagues, api_endpoints):
        response = GET_request(api_url + endpoint_str, api_headers, max_retries=6)
        destination_blob_name = api_league + "_" + api_endpoint + ".json"
        extract_blob(storage_client=google_cloud_client,
                     bucket_name=os.environ["BUCKET_NAME"],
                     source_string=response_str(response),
                     destination_blob_name=destination_blob_name,
                     location=os.environ["LOCATION"])
