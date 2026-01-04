import requests
import json
import os
import sys
from datetime import datetime
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core.exceptions import AzureError

# NIH Clinical Tables Search API (HCPCS)
API_URL = "https://clinicaltables.nlm.nih.gov/api/hcpcs/v3/search"

def fetch_hcpcs_data(term="office visit", limit=50):
    print(f"Fetching HCPCS/CPT data for term: {term}...")
    params = {
        'terms': term,
        'maxList': limit
    }
    
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        codes = data[1]
        results = []
        for i in range(len(codes)):
            results.append({
                "code": codes[i],
                "description": data[3][i] if len(data) > 3 else ""
            })
            
        print(f"Successfully retrieved {len(results)} records.")
        return results
        
    except Exception as e:
        print(f"Error fetching HCPCS data: {e}", file=sys.stderr)
        return []

def upload_to_adls(data, storage_account_name, storage_account_key, container_name):
    try:
        service_client = DataLakeServiceClient(
            account_url=f"https://{storage_account_name}.dfs.core.windows.net",
            credential=storage_account_key
        )
        file_system_client = service_client.get_file_system_client(file_system=container_name)
        
        directory_name = "cpt_data"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"cpt_extract_{timestamp}.json"
        
        file_client = file_system_client.get_file_client(f"{directory_name}/{file_name}")
        json_data = json.dumps(data)
        
        print(f"Uploading {file_name} to container {container_name}...")
        file_client.create_file()
        file_client.append_data(data=json_data, offset=0, length=len(json_data))
        file_client.flush_data(len(json_data))
        
        print(f"Successfully uploaded to {container_name}/{directory_name}/{file_name}")
        
    except Exception as e:
        print(f"Error uploading to ADLS: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")
    storage_account_key = os.getenv("STORAGE_ACCOUNT_KEY")
    container_name = os.getenv("CONTAINER_NAME", "landing")
    
    data = fetch_hcpcs_data(limit=100)
    
    if data and storage_account_name and storage_account_key:
        upload_to_adls(data, storage_account_name, storage_account_key, container_name)
    else:
        print("Data extraction complete (no upload).")
