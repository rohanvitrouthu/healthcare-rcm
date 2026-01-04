import requests
import pandas as pd
import json
import time
import os
import sys
from datetime import datetime
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core.exceptions import AzureError

# NPPES NPI Registry API Endpoint
API_URL = "https://npiregistry.cms.hhs.gov/api/?version=2.1"

def fetch_npi_data(limit=10):
    """
    Fetches a batch of NPI data for Cardiology taxonomy.
    """
    params = {
        'taxonomy_description': 'Cardiology',
        'limit': limit,
        'pretty': 'on'
    }
    
    print(f"Fetching {limit} records from NPI Registry...")
    
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = data.get('results', [])
        print(f"Successfully retrieved {len(results)} records.")
        
        return results
        
    except Exception as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        return []

def upload_to_adls(data, storage_account_name, storage_account_key, container_name):
    """
    Uploads data to ADLS Gen2.
    """
    try:
        service_client = DataLakeServiceClient(
            account_url=f"https://{storage_account_name}.dfs.core.windows.net",
            credential=storage_account_key
        )
        
        file_system_client = service_client.get_file_system_client(file_system=container_name)
        
        directory_name = "npi_data"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"npi_extract_{timestamp}.json"
        
        file_client = file_system_client.get_file_client(f"{directory_name}/{file_name}")
        
        # Convert list of dicts to newline-delimited JSON or just a JSON array
        json_data = json.dumps(data)
        
        print(f"Uploading {file_name} to container {container_name}...")
        file_client.create_file()
        file_client.append_data(data=json_data, offset=0, length=len(json_data))
        file_client.flush_data(len(json_data))
        
        print(f"Successfully uploaded to {container_name}/{directory_name}/{file_name}")
        
    except AzureError as e:
        print(f"Azure Storage Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error uploading to ADLS: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    print("Starting NPI Extractor Job...")
    
    # Configuration from environment variables
    storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")
    storage_account_key = os.getenv("STORAGE_ACCOUNT_KEY")
    container_name = os.getenv("CONTAINER_NAME", "landing")
    
    if not storage_account_name or not storage_account_key:
        print("Error: STORAGE_ACCOUNT_NAME or STORAGE_ACCOUNT_KEY environment variables not set.", file=sys.stderr)
        # We don't exit here if we just want to test fetching, but for production we should.
        # sys.exit(1)
    
    data = fetch_npi_data(limit=50)
    
    if data:
        print(f"Data extraction complete. {len(data)} records found.")
        if storage_account_name and storage_account_key:
            upload_to_adls(data, storage_account_name, storage_account_key, container_name)
        else:
            print("Skipping upload due to missing credentials.")
    else:
        print("No data extracted.", file=sys.stderr)
        sys.exit(1)