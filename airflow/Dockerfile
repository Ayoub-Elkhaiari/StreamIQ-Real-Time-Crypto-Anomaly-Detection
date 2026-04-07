FROM apache/airflow:2.8.0

USER airflow

RUN pip install --no-cache-dir \
    requests \
    psycopg2-binary \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.0/constraints-3.11.txt"