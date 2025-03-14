from api_source_access import *

"""
from pathlib import Path

project_directory = str(Path.cwd().parent)
dbt_scripts_directory = project_directory + "/" + "dbt_scripts"

from dbt_configuration import *

project_directory = str(Path.cwd().parent)
dbt_scripts_directory = project_directory + "/" + "dbt_scripts"

profiles_yaml = get_profiles_yaml(4)
create_yaml(profiles_yaml, dbt_scripts_directory, "profiles")

project_directory = str(Path.cwd().parent)
dbt_scripts_directory = project_directory + "/" + "dbt_scripts"
dbt_seeds_directory = dbt_scripts_directory + "/" + "seeds"
"""

dbt_seeds_directory = "/opt/dbt_scripts/seeds"

api_url, _, api_seed_resources, _, _ = parse_api_config('/opt/config.yml')  # "../config.yml"
api_headers = get_api_headers()

if api_seed_resources:
    for seed_resource, endpoint_str in api_seed_resource_endpoint_generator(api_seed_resources):
        if seed_resource == "areas":
            response = GET_request(api_url + endpoint_str, api_headers, max_retries=6)
            areas_df = standardize_seed_areas_response(response)
            seed_df_extract(dbt_seeds_directory, areas_df, file_name="area")
        else:
            raise NotImplementedError(f"Seed resource {seed_resource} is not implemented yet.")
