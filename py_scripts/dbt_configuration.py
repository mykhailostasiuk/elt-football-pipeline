import os
import yaml


def get_profiles_yaml(threads):
    yaml_content = {
        "dbt_scripts": {
            "target": "dev",
            "outputs": {
                "dev": {
                    "type": "bigquery",
                    "method": "oauth",
                    "project": os.getenv("GOOGLE_CLOUD_PROJECT"),
                    "dataset": os.getenv("WAREHOUSE_NAME"),
                    "threads": threads,
                    "OPTIONAL_CONFIG": "VALUE",
                }
            }
        }
    }

    return yaml_content


def get_schema_yaml(table_names_list):
    yaml_content = {
        "version": 2,
        "sources": [
            {
                "name": "football_raw",
                "database": os.getenv("GOOGLE_CLOUD_PROJECT"),
                "schema": os.getenv("WAREHOUSE_NAME") + "_raw",
                "tables": [{"name": table_name, "description": f"Source table {table_name}"} for table_name in table_names_list]
            }
        ]
    }

    return yaml_content


def get_metadata_sql_macros(table_names_list):
    sql_content = """
    {% macro matches_table_names() %}
        {% set table_names = [matches_table_list] %}
        {% do return(table_names) %}
    {% endmacro %}

    {% macro teams_table_names() %}
        {% set table_names = [teams_table_list] %}
        {% do return(table_names) %}
    {% endmacro %}
    """

    matches_table_list = [table_name for table_name in table_names_list if table_name.endswith('_matches')]
    teams_table_list = [table_name for table_name in table_names_list if table_name.endswith('_teams')]

    matches_table_str = ', '.join(f"'{table}'" for table in matches_table_list)
    teams_table_str = ', '.join(f"'{table}'" for table in teams_table_list)

    sql_content = sql_content.replace("matches_table_list", matches_table_str)
    sql_content = sql_content.replace("teams_table_list", teams_table_str)

    return sql_content


def create_yaml(yaml_content, directory, file_name):
    file_path = os.path.join(directory, file_name + ".yml")

    with open(file_path, 'w') as file:
        yaml.dump(yaml_content, file, default_flow_style=False)

    print(f"{file_name}.yml file was set up at {directory}.")


def create_sql_macros(sql_content, directory, file_name):
    file_path = os.path.join(directory, file_name + ".sql")

    with open(file_path, 'w') as file:
        file.write(sql_content)

    print(f"{file_name}.sql file was set up at {directory}.")
