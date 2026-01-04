from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.hooks.base import BaseHook
from datetime import datetime, timedelta

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
    'npi_healthcare_pipeline',
    default_args=default_args,
    description='Full NPI Pipeline: Extraction to Bronze',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['healthcare', 'npi', 'bronze'],
) as dag:

    # 1. Extract from CMS API to Landing (JSON)
    extract_npi_to_landing = KubernetesPodOperator(
        task_id='extract_npi_to_landing',
        name='npi-extractor',
        namespace='airflow',
        image='acrhealthcarercmdev.azurecr.io/npi-extractor:v2',
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

    # 2. Process from Landing to Bronze (Parquet)
    process_landing_to_bronze = KubernetesPodOperator(
        task_id='process_landing_to_bronze',
        name='npi-bronze-processor',
        namespace='airflow',
        image='acrhealthcarercmdev.azurecr.io/npi-bronze-processor:v1',
        env_vars={
            'STORAGE_ACCOUNT_NAME': STORAGE_ACCOUNT_NAME,
            'STORAGE_ACCOUNT_KEY': STORAGE_ACCOUNT_KEY,
        },
        resources={
            'request_cpu': '200m',
            'request_memory': '256Mi',
            'limit_cpu': '500m',
            'limit_memory': '512Mi',
        },
        is_delete_operator_pod=True,
        get_logs=True,
    )

    # 3. Data Quality Check on Bronze
    validate_bronze_data = KubernetesPodOperator(
        task_id='validate_bronze_data',
        name='npi-data-quality',
        namespace='airflow',
        image='acrhealthcarercmdev.azurecr.io/npi-data-quality:v1',
        env_vars={
            'STORAGE_ACCOUNT_NAME': STORAGE_ACCOUNT_NAME,
            'STORAGE_ACCOUNT_KEY': STORAGE_ACCOUNT_KEY,
        },
        resources={
            'request_cpu': '200m',
            'request_memory': '256Mi',
            'limit_cpu': '500m',
            'limit_memory': '512Mi',
        },
        is_delete_operator_pod=True,
        get_logs=True,
    )

    extract_npi_to_landing >> process_landing_to_bronze >> validate_bronze_data
