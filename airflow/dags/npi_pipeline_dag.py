from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
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

# Databricks Cluster Config (Small/Cheap)
new_cluster_config = {
    "spark_version": "14.3.x-scala2.12",
    "node_type_id": "Standard_DS3_v2",
    "num_workers": 1,
    "azure_attributes": {
        "availability": "SPOT_WITH_FALLBACK_AZURE"
    }
}

with DAG(
    'npi_healthcare_pipeline',
    default_args=default_args,
    description='Full NPI Pipeline: Extraction to Silver via Databricks',
    schedule=timedelta(days=1),
    catchup=False,
    tags=['healthcare', 'npi', 'bronze', 'silver', 'databricks'],
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
        is_delete_operator_pod=True,
        get_logs=True,
    )

    # 4. Bronze to Silver Transformation (Databricks)
    bronze_to_silver_databricks = DatabricksSubmitRunOperator(
        task_id='bronze_to_silver_databricks',
        new_cluster=new_cluster_config,
        notebook_task={
            'notebook_path': '/Shared/healthcare_rcm/bronze_to_silver_npi',
            'base_parameters': {
                'storage_account_name': STORAGE_ACCOUNT_NAME,
                'storage_account_key': STORAGE_ACCOUNT_KEY
            }
        }
    )

    # 5. Silver to Gold Transformation (Databricks)
    silver_to_gold_databricks = DatabricksSubmitRunOperator(
        task_id='silver_to_gold_databricks',
        new_cluster=new_cluster_config,
        notebook_task={
            'notebook_path': '/Shared/healthcare_rcm/silver_to_gold_npi',
            'base_parameters': {
                'storage_account_name': STORAGE_ACCOUNT_NAME,
                'storage_account_key': STORAGE_ACCOUNT_KEY
            }
        }
    )

    extract_npi_to_landing >> process_landing_to_bronze >> validate_bronze_data >> bronze_to_silver_databricks >> silver_to_gold_databricks
