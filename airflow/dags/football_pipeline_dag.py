from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from pathlib import Path
import sys
import os

sys.path.append('/opt/py_scripts')

from dbt_configuration import create_yaml, get_profiles_yaml

dbt_scripts_directory = '/opt/dbt_scripts'
python_scripts_directory = '/opt/py_scripts'


def check_profiles_yaml():
    if not os.path.exists('/opt/dbt_scripts/profiles.yaml'):
        profiles_yaml = get_profiles_yaml(4)
        create_yaml(profiles_yaml, dbt_scripts_directory, "profiles")


default_args = {
    "owner": "airflow",
    "depends_on_past": True,
    "start_date": days_ago(1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

dag = DAG(
    'football_pipeline_dag',
    default_args=default_args,
    description='ELT football pipeline',
    schedule_interval="0 0 * * *",
    catchup=False
)

check_profiles = PythonOperator(
    task_id='check_profiles',
    python_callable=check_profiles_yaml,
    dag=dag
)

extract = BashOperator(
    task_id='extract',
    bash_command=f'python {python_scripts_directory}/extract.py',
    dag=dag
)

load = BashOperator(
    task_id='load',
    bash_command=f'python {python_scripts_directory}/load.py',
    dag=dag
)

dbt_build = BashOperator(
    task_id="dbt_build",
    bash_command=f"cd {dbt_scripts_directory} && dbt clean && dbt build --exclude seed",
    dag=dag
)

monthly_dag = DAG(
    'football_pipeline_dag_monthly',
    default_args=default_args,
    description='Monthly ELT football pipeline',
    schedule_interval='@monthly',
    catchup=False
)

check_profiles_monthly = PythonOperator(
    task_id='check_profiles_monthly',
    python_callable=check_profiles_yaml,
    dag=monthly_dag
)

extract_seed = BashOperator(
    task_id="extract_seed",
    bash_command=f"python {python_scripts_directory}/extract_seed.py",
    dag=monthly_dag
)

dbt_seed = BashOperator(
    task_id="dbt_seed",
    bash_command=f"cd {dbt_scripts_directory} && dbt clean && dbt seed && dbt test --select seed",
    dag=monthly_dag
)

check_profiles_monthly >> extract_seed >> dbt_seed
check_profiles >> extract >> load >> dbt_build
