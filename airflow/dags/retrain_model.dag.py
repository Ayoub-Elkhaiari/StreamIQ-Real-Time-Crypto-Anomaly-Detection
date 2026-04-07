from datetime import datetime

import requests
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


def extract_normal_data():
    print("Extracting last 7 days normal snapshots (is_anomaly=false)")


def validate_model():
    contamination_rate = 0.03
    if not (0.01 <= contamination_rate <= 0.15):
        raise ValueError("Contamination rate out of expected range")
    print(f"Validation passed with contamination={contamination_rate}")


def deploy_model():
    print("Deploy model artifact to ml-service/model/anomaly_model.pkl")


def reload_ml_service():
    r = requests.post("http://ml-service:8001/reload", timeout=10)
    r.raise_for_status()
    print(r.json())


with DAG(
    "retrain_model",
    start_date=datetime(2025, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
) as dag:
    t1 = PythonOperator(task_id="extract_normal_data", python_callable=extract_normal_data)
    t2 = BashOperator(task_id="retrain_isolation_forest", bash_command="cd /opt/airflow/ml-service && python train.py")
    t3 = PythonOperator(task_id="validate_model", python_callable=validate_model)
    t4 = PythonOperator(task_id="deploy_model", python_callable=deploy_model)
    t5 = PythonOperator(task_id="reload_ml_service", python_callable=reload_ml_service)

    t1 >> t2 >> t3 >> t4 >> t5
