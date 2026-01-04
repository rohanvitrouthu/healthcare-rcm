from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.hooks.base import BaseHook
from datetime import datetime, timedelta
from kubernetes.client import models as k8s

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Fetch connection details from Airflow
try:
    conn = BaseHook.get_connection('azure_adls_landing')
    STORAGE_ACCOUNT_NAME = conn.login
    STORAGE_ACCOUNT_KEY = conn.password
except Exception:
    STORAGE_ACCOUNT_NAME = "missing"
    STORAGE_ACCOUNT_KEY = "missing"

with DAG(
    'npi_k8s_extractor_to_adls',
    default_args=default_args,
    description='Extract NPI data using KubernetesPodOperator and load to ADLS Gen2',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['healthcare', 'npi', 'k8s'],
) as dag:

    npi_extract_k8s = KubernetesPodOperator(
        task_id='npi_extract_k8s',
        name='npi-extractor-pod',
        namespace='airflow', # Assuming Airflow is in 'airflow' namespace
        image='acrhealthcarercmdev.azurecr.io/npi-extractor:v2', # We will build v2
        env_vars={
            'STORAGE_ACCOUNT_NAME': STORAGE_ACCOUNT_NAME,
            'STORAGE_ACCOUNT_KEY': STORAGE_ACCOUNT_KEY,
            'CONTAINER_NAME': 'landing',
        },
        resources={
            'request_cpu': '100m',
            'request_memory': '128Mi',
            'limit_cpu': '200m',
            'limit_memory': '256Mi',
        },
        is_delete_operator_pod=True,
        get_logs=True,
    )

    npi_extract_k8s
