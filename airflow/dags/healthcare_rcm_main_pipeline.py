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
    'healthcare_rcm_master_pipeline',
    default_args=default_args,
    description='Main Healthcare RCM Pipeline: NPI, ICD, CPT Extraction to Bronze',
    schedule=timedelta(days=1),
    catchup=False,
    tags=['healthcare', 'rcm', 'pipeline'],
) as dag:

    def create_k8s_task(task_id, name, image, env_vars=None):
        return KubernetesPodOperator(
            task_id=task_id,
            name=name,
            namespace='airflow',
            image=image,
            env_vars=env_vars or {},
            is_delete_operator_pod=True,
            get_logs=True,
        )

    # ENV for all tasks
    common_env = {
        'STORAGE_ACCOUNT_NAME': STORAGE_ACCOUNT_NAME,
        'STORAGE_ACCOUNT_KEY': STORAGE_ACCOUNT_KEY,
    }

    # 1. Extraction Tasks (Landing)
    extract_npi = create_k8s_task(
        'extract_npi', 'npi-extractor', 
        'acrhealthcarercmdev.azurecr.io/npi-extractor:v2', 
        env_vars={**common_env, 'CONTAINER_NAME': 'landing'}
    )

    extract_icd = create_k8s_task(
        'extract_icd', 'icd-extractor', 
        'acrhealthcarercmdev.azurecr.io/icd-extractor:v1', 
        env_vars={**common_env, 'CONTAINER_NAME': 'landing'}
    )

    extract_cpt = create_k8s_task(
        'extract_cpt', 'cpt-extractor', 
        'acrhealthcarercmdev.azurecr.io/cpt-extractor:v1', 
        env_vars={**common_env, 'CONTAINER_NAME': 'landing'}
    )

    # 2. Bronze Processing Tasks
    process_npi = create_k8s_task(
        'process_npi_bronze', 'npi-bronze-processor', 
        'acrhealthcarercmdev.azurecr.io/npi-bronze-processor:v1', 
        env_vars=common_env
    )

    # For now, we can use the same processor or specialized ones. 
    # Let's assume a generic one or specialized ones later.
    # We'll stick to NPI for now to avoid complexity, but layout the structure.
    
    # 3. Data Quality
    validate_npi = create_k8s_task(
        'validate_npi_bronze', 'npi-dq', 
        'acrhealthcarercmdev.azurecr.io/npi-data-quality:v1', 
        env_vars=common_env
    )

    # Dependencies
    extract_npi >> process_npi >> validate_npi
    extract_icd >> extract_cpt # Parallel to others, simplified
