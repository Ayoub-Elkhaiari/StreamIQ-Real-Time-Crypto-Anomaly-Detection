from datetime import datetime

import psycopg2
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator

POSTGRES = dict(host="postgres", database="streamiq", user="streamiq", password="streamiq123")
COINGECKO_URL = "https://api.coingecko.com/api/v3/ping"


def check_kafka_health():
    print("Kafka broker health check placeholder: kafka-broker:9092")


def check_ml_service_health():
    r = requests.get("http://ml-service:8001/health", timeout=5)
    r.raise_for_status()
    print(r.json())


def check_postgres_health():
    with psycopg2.connect(**POSTGRES) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            print(cur.fetchone())


def check_coingecko_health():
    r = requests.get(COINGECKO_URL, timeout=10)
    r.raise_for_status()
    print("CoinGecko reachable")


def log_anomaly_rate():
    with psycopg2.connect(**POSTGRES) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*), COALESCE(SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END),0)
                FROM coin_snapshots
                WHERE processed_at >= NOW() - interval '1 hour'
                """
            )
            total, anomalies = cur.fetchone()
            rate = (anomalies / total * 100) if total else 0.0
            if rate > 10:
                print(f"WARNING anomaly rate high: {rate:.2f}%")
            else:
                print(f"Anomaly rate normal: {rate:.2f}%")


with DAG(
    "streamiq_health",
    start_date=datetime(2025, 1, 1),
    schedule="@hourly",
    catchup=False,
) as dag:
    t1 = PythonOperator(task_id="check_kafka_health", python_callable=check_kafka_health)
    t2 = PythonOperator(task_id="check_ml_service_health", python_callable=check_ml_service_health)
    t3 = PythonOperator(task_id="check_postgres_health", python_callable=check_postgres_health)
    t4 = PythonOperator(task_id="check_coingecko_health", python_callable=check_coingecko_health)
    t5 = PythonOperator(task_id="log_anomaly_rate", python_callable=log_anomaly_rate)

    [t1, t2, t3, t4] >> t5
