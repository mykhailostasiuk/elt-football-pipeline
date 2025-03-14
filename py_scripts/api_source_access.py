import os
import requests
import json
import yaml
import itertools
import time
import requests.exceptions
import pandas as pd


def parse_api_config(config_file):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)

    required_keys = ["api_url"]
    optional_keys = ["api_resources", "api_seed_resources", "api_leagues", "api_endpoints"]

    config_data = {key: config.get(key) for key in required_keys + optional_keys}

    if config_data["api_url"] is None:
        raise ValueError("No api_url was provided.")

    if not config_data["api_resources"] and not config_data["api_seed_resources"]:
        raise ValueError("No api_resources or api_seed_resources were provided.")

    def extract_values(data, key):
        if data is None:
            return None
        values = list(data.values())
        if any(value is None for value in values):
            raise ValueError(f"One of the {key} values was not provided.")
        return values

    api_resources = extract_values(config_data["api_resources"], "api_resources")
    api_seed_resources = extract_values(config_data["api_seed_resources"], "api_seed_resources")
    api_leagues = extract_values(config_data["api_leagues"], "api_leagues")
    api_endpoints = extract_values(config_data["api_endpoints"], "api_endpoints")

    if api_resources and (api_leagues is None or api_endpoints is None):
        raise ValueError("No values for api_resources or api_leagues were provided.")

    return config_data["api_url"], api_resources, api_seed_resources, api_leagues, api_endpoints


def api_resource_endpoint_generator(api_resources, api_leagues, api_endpoints):
    for resource, league, endpoint in itertools.product(api_resources, api_leagues, api_endpoints):
        endpoint_str = f'/{resource}/{league}/{endpoint}'
        yield resource, league, endpoint, endpoint_str


def api_seed_resource_endpoint_generator(api_seed_resources):
    for seed_resource in api_seed_resources:
        endpoint_str = f'/{seed_resource}'
        yield seed_resource, endpoint_str


def get_api_headers():
    API_AUTHORIZATION_METHOD = os.getenv("API_AUTHORIZATION_METHOD")
    API_KEY = os.getenv("API_KEY")
    headers = {API_AUTHORIZATION_METHOD: API_KEY} if API_AUTHORIZATION_METHOD and API_KEY else {}
    return headers


def GET_request(url, headers, max_retries=5, base_delay=2):
    retries = 0
    while retries < max_retries:
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            wait_time = base_delay * (2 ** retries)
            print(f"API rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            retries += 1
        else:
            response.raise_for_status()
            return response
    raise requests.exceptions.RetryError(f"Maximum number of retries reached.")


def response_json(response):
    return response.json()


def response_str(response):
    return json.dumps(response_json(response))


def seed_df_extract(dbt_seeds_directory, seed_df, file_name):
    file_name = f"dim_{file_name}.csv"
    file_path = os.path.join(dbt_seeds_directory, file_name )

    seed_df.to_csv(file_path, index=False)

    print(f"{file_name} file was set up at {dbt_seeds_directory}")


def standardize_seed_areas_response(seed_areas_response):
    normalized_data = pd.json_normalize(response_json(seed_areas_response), record_path="areas")[['id', 'name', 'flag', 'parentArea']]
    return normalized_data.rename(columns={"parentArea": "location", "id": "area_id"})
