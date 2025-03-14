FROM apache/airflow:latest

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --use-deprecated=legacy-resolver -r requirements.txt
