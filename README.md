# Football Data ELT Pipeline

## Overview
This project is an ELT (Extract, Load, Transform) pipeline designed to ingest, store, and process football match data from various European leagues, including the UEFA Champions League. It leverages Python, Apache Airflow, Google Cloud Storage (GCS), BigQuery, DBT, and Docker to automate data ingestion and transformation.

The pipeline extracts match data from an external football API, stages raw JSON files in a GCS bucket, creates CSV files for the rarely updated data, and loads them into BigQuery as external tables. DBT then transforms the data into a structured Snowflake schema within the data warehouse, creating dimension tables for teams, seasons, and competitions. The leagues processed can be adjusted in the `config.yml` file when using an API subscription that supports additional leagues.

## Architecture Overview
![Architecture](/assets/architecture.jpeg)

The ELT pipeline consists of the following steps:

1. **Data Ingestion**: Football data is extracted from an external API and stored as JSON files in a Google Cloud Storage (GCS) staging bucket. Rarely changed data is stored as CSV files inside a dbt `seed` folder. 
2. **Loading**: BigQuery creates external tables that reference the JSON files in the staging bucket.
3. **Transformation**: dbt builds a Snowflake schema in BigQuery to transform raw data into an optimized structure for analytics.
4. **Orchestration**: Apache Airflow manages and automates the pipeline workflows.
5. **Docker**: Containerizes the Airflow environment for easy deployment and reproducibility.

## Data Warehouse Model Overview
![Snowflake model](/assets/snowflake.jpeg)

The data warehouse follows a **Snowflake schema**, with a central fact table that records match details, and several dimension tables providing additional context:

#### Fact table
- `fact_matches`: Stores key match data, including:
  - Match metadata (`match_id`, `competition_id`, `season_id`, `datetime_id`, `area_id`).
  - Home and away teams (`home_team_id`, `away_team_id`).
  - Scores at halftime and full-time.
  - Match outcome (`winner`, `duration`, `status`).
  - Additional details (`season_matchday`, `competition_stage`, `competition_group`).
#### Dimensional tables
- `dim_team`: Contains information about teams, including name, emblem, colors, foundation year, website, and stadium.
- `dim_season`: Stores season details such as start and end dates, match counts, and competition status.
- `dim_competition`: Holds league and tournament data, including competition type and emblem.
- `dim_area`: Represents geographical locations associated with teams and competitions.
- `dim_datetime`: Provides time-based attributes for matches, breaking down timestamps into year, quarter, month, day, week, weekday, and exact time components.


## Prerequisites
#### API
Make sure you have an account on [Football-Data.org](https://www.football-data.org/). You can sign up [here](https://www.football-data.org/client/register) to get access.

#### Google Cloud Platform 

Make sure you have a Google Cloud Platform account and a project:  

- [Set up a GCP project](https://console.cloud.google.com/projectcreate?previousPage=%2Fprojectselector2%2Fapis%2Fdashboard%3Finv%3D1%26invt%3DAbsCpQ%26supportedpurview%3Dproject&organizationId=0&inv=1&invt=AbsCpQ&supportedpurview=project)

Make sure you have enabled the BigQuery API:

- [Enable BigQuery API](https://console.cloud.google.com/apis/api/bigquery.googleapis.com)

Make sure you have enabled the Google Cloud Storage API:
- [Enable GCS API](https://console.cloud.google.com/apis/api/storage-component.googleapis.com/)

#### Google Cloud SDK
Make sure you have an access to the Google Cloud CLI commands:
- [Google Cloud SDK Installation Guide](https://cloud.google.com/sdk/docs/install)

Verify the existance of the Google Cloud SDK:
```
gcloud --version
```

#### Docker & Docker Compose
Make sure you have the Docker and Docker Compose installed on your system:
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

Verify the existance of the Docker and Docker Compose:
```
docker --version
docker-compose --version
```

## Getting Started

#### 1. Get the API token
After the registration on [Football-Data.org](https://www.football-data.org/) you receive the mail with your API token. You can also observe it in your account settings.

#### 2. Get the Google Application Default Credentials 
Authenticate with your Google account:

```
gcloud auth login
```
Set the Google Cloud Platform project:
```
gcloud config set project your_project_id
```

Generate `application_default_credentials.json` file:
```
gcloud auth application-default login
```
This will output the path to your Google ADC file:
```
Credentials saved to file: [/path/to/your/application_default_credentials.json]
```
#### 3. Clone the repository
Create or navigate to the (empty) folder where you want to store the project:
```
cd /path/to/your/project
```
Clone the `elt-football-pipeline` repository and navigate to the root directory of the project:
```
git clone https://github.com/mykhailostasiuk/elt-football-pipeline.git
cd elt-football-pipeline
```

#### 4. Configurate the Google dependencies
Copy the previously obtained Google ADC file `application_default_credentials.json` to the root directory of the project:
```
copy /path/to/your/application_default_credentials.json /path/to/your/project/elt-football-pipeline
```
Create a `.env` file in the root directory of the project with the following content:
```
API_AUTHORIZATION_METHOD = 'X-Auth-Token'
API_KEY = 'your-api-token'
GOOGLE_CLOUD_PROJECT = "your_project_id"
WAREHOUSE_NAME = "big-query-dataset-name"
BUCKET_NAME = "google-cloud-storage-bucket-name"
LOCATION = "project-location"
AIRFLOW_IMAGE_NAME = apache/airflow:latest
AIRFLOW_UID = 50000
```
Where:
- `your-api-token` is the previously obtained API token of the API provider.
- `your_project_id` is the previously created Google Cloud project id.
- `big-query-dataset-name` is the name of the destination BigQuery warehouse.
- `google-cloud-storage-bucket-name` is the name of the Google Cloud Storage staging bucket.
- `project-location` is the name of the project location on the Google Cloud Platform.

It doesn't matter if the BigQuery dataset `big-query-dataset-name` and Google Cloud Storage bucket `google-cloud-storage-bucket-name` exist or not, they will be created if they don't.

Example of the `.env` file setup:

```
API_AUTHORIZATION_METHOD = 'X-Auth-Token'
API_KEY = '534523945734hr5723h4kh5gf63'
GOOGLE_CLOUD_PROJECT = "my-football-pipeline-project"
WAREHOUSE_NAME = "football-warehouse"
BUCKET_NAME = "football-bucket"
LOCATION = "europe-west6"
AIRFLOW_IMAGE_NAME = apache/airflow:latest
AIRFLOW_UID = 50000
```

#### 5. Start the Docker services
Build the Docker image and start the Docker services:
```
docker-compose up --build -d
```

Verify if the composed container stack is running:
```
docker ps
```

You should see an output similar to the following:

```
CONTAINER ID   IMAGE                   COMMAND                  CREATED         STATUS                   PORTS                    NAMES
c135925c03f5   apache/airflow:latest   "/usr/bin/dumb-init …"   4 minutes ago   Up 4 minutes (healthy)   8080/tcp                 elt-football-pipeline-airflow-triggerer-1
0c71e4e4217f   apache/airflow:latest   "/usr/bin/dumb-init …"   4 minutes ago   Up 4 minutes (healthy)   0.0.0.0:8080->8080/tcp   elt-football-pipeline-airflow-webserver-1
1b23d1d7e692   apache/airflow:latest   "/usr/bin/dumb-init …"   4 minutes ago   Up 4 minutes (healthy)   8080/tcp                 elt-football-pipeline-airflow-worker-1
7b02fbdee762   apache/airflow:latest   "/usr/bin/dumb-init …"   4 minutes ago   Up 4 minutes (healthy)   8080/tcp                 elt-football-pipeline-airflow-scheduler-1
02d0e407a5f7   redis:7.2-bookworm      "docker-entrypoint.s…"   4 minutes ago   Up 4 minutes (healthy)   6379/tcp                 elt-football-pipeline-redis-1
0bd6a14216f9   postgres:13             "docker-entrypoint.s…"   4 minutes ago   Up 4 minutes (healthy)   5432/tcp                 elt-football-pipeline-postgres-1
```

To stop the running container stack, run the following command:
```
docker-compose -p elt-football-pipeline stop
```
To (re)run/re-create already built container stack, run the following command:
```
docker-compose -p elt-football-pipeline up -d
```
To remove the container stack, run the following command:
```
docker-compose -p elt-football-pipeline down
```
#### 6. Start the Airflow DAGs
**To access the Airflow the Docker container stack should be running.**
From the list of running containers find the `CONTAINER ID` of the container `elt-football-pipeline-airflow-webserver-1`:
```
docker ps

CONTAINER ID   IMAGE                   COMMAND                  CREATED         STATUS                   PORTS                    NAMES
...
0c71e4e4217f   apache/airflow:latest   "/usr/bin/dumb-init …"   4 minutes ago   Up 4 minutes (healthy)   0.0.0.0:8080->8080/tcp   elt-football-pipeline-airflow-webserver-1
...
```
Here the `CONTAINER ID` is `0c71e4e4217f`.

Enter the above container's environment:
```
docker exec -it 0c71e4e4217f bash
```
Inside the container's environment list the Airflow DAGs:

```
airflow dags list
```
You should see an output similar to the following:
```
dag_id                        | fileloc                                    | owners  | is_paused
==============================+============================================+=========+==========
football_pipeline_dag         | /opt/airflow/dags/football_pipeline_dag.py | airflow | True
football_pipeline_dag_monthly | /opt/airflow/dags/football_pipeline_dag.py | airflow | True
```
Since on the very start the Airflow DAGs are paused - unpause them:
```
airflow dags unpause football_pipeline_dag
airflow dags unpause football_pipeline_dag_monthly
```
You should see an output similar to the following:
```
dag_id                        | fileloc                                    | owners  | is_paused
==============================+============================================+=========+==========
football_pipeline_dag         | /opt/airflow/dags/football_pipeline_dag.py | airflow | False
football_pipeline_dag_monthly | /opt/airflow/dags/football_pipeline_dag.py | airflow | False
```
Make the initial `football_pipeline_dag_monthly` trigger:
```
airflow dags trigger football_pipeline_dag_monthly
```
Ensure that the trigger run succesfully:
```
airflow dags list-runs -d football_pipeline_dag_monthly
```
You should see an output similar to the following:
```
dag_id               | run_id              | state   | execution_date      | start_date         | end_date
=====================+=====================+=========+=====================+====================+=====================
football_pipeline_da | manual__2025-03-14T | success | 2025-03-14T22:39:21 | 2025-03-14T22:39:2 | 2025-03-14T22:39:50.
g_monthly            | 22:39:21+00:00      |         | +00:00              | 1.868267+00:00     | 973175+00:00
```
Make the initial `football_pipeline_dag` trigger:
```
airflow dags trigger football_pipeline_dag
```
Ensure that the trigger run succesfully:
```
airflow dags list-runs -d football_pipeline_dag
```
You should see an output similar to the following:
```
dag_id               | run_id              | state   | execution_date      | start_date         | end_date
=====================+=====================+=========+=====================+====================+=====================
football_pipeline_da | manual__2025-03-14T | success | 2025-03-14T22:43:49 | 2025-03-14T22:43:4 | 2025-03-14T22:46:57.
g                    | 22:43:49+00:00      |         | +00:00              | 9.882627+00:00     | 238070+00:00
```

#### Alternatively: Login to the Airflow UI
**To access the Airflow UI the Docker container stack should be running.**
Access the running Airflow environment using Airflow UI by going to `localhost:8080` on a web browser:

```
start http://localhost:8080
```
On the Airflow login page use the following default login credentials:
- Username: `airflow`
- Password: `airflow`

Once logged in, you should land on the **DAGs** page, which lists all available DAGs.
Unpause the DAGs and trigger them manually in the following order:

1. `football_pipeline_dag_monthly`
2. `football_pipeline_dag`

To trigger the DAG manually, click on the **Trigger DAG** button located under the **Actions** column for the selected DAG. After triggering, the DAG will begin running. You can click on the DAG name to go to the **DAG Details** page. On the DAG Details page, you can monitor the progress of each task in the DAG. Tasks will be colored based on their status (e.g., green for success, red for failure, yellow for running).

To view detailed logs for any task click the **View Logs** button to see detailed information about the task's execution.

**Running Airflow DAGs may take some time.**

**Congratulations!** You have successfully run and orchestrated the `elt-football-pipeline`. You can now see your ingested data in the previously specified BigQuery warehouse.
