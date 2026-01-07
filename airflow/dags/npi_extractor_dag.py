from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
from datetime import datetime, timedelta
import requests
import json

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def extract_npi_data(**kwargs):
    # CMS NPPES API endpoint
    url = "https://npiregistry.cms.hhs.gov/api/?version=2.1&city=Baltimore&state=MD"
    response = requests.get(url)
    data = response.json()
    
    # Push data to XCom or return it
    return data

def load_to_adls(ti, **kwargs):
    data = ti.xcom_pull(task_ids='extract_npi_data')
    
    # Use WasbHook (for Blob Storage/ADLS Gen2 with Blob API)
    # Connection ID 'azure_adls_landing' must be configured in Airflow
    hook = WasbHook(wasb_conn_id='azure_adls_landing')
    
    container_name = 'landing'
    blob_name = f'npi_data/npi_extract_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    hook.load_string(
        string_data=json.dumps(data),
        container_name=container_name,
        blob_name=blob_name,
        overwrite=True
    )
    print(f"Successfully uploaded to {container_name}/{blob_name}")

with DAG(
    'npi_extractor_to_adls',
    default_args=default_args,
    description='Extract NPI data and load to ADLS Gen2',
    schedule=timedelta(days=1),
    catchup=False,
) as dag:

    extract_task = PythonOperator(
        task_id='extract_npi_data',
        python_callable=extract_npi_data,
    )

    load_task = PythonOperator(
        task_id='load_to_adls',
        python_callable=load_to_adls,
    )

    extract_task >> load_task
