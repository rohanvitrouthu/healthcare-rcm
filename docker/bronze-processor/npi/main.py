import os
import sys
import pandas as pd
import json
from datetime import datetime
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core.exceptions import AzureError
import io

def get_service_client(storage_account_name, storage_account_key):
    return DataLakeServiceClient(
        account_url=f"https://{storage_account_name}.dfs.core.windows.net",
        credential=storage_account_key
    )

def process_npi_landing_to_bronze(storage_account_name, storage_account_key):
    service_client = get_service_client(storage_account_name, storage_account_key)
    
    landing_fs = service_client.get_file_system_client(file_system="landing")
    bronze_fs = service_client.get_file_system_client(file_system="bronze")
    
    landing_path = "npi_data"
    bronze_path = "npi_data"
    
    print(f"Checking for new files in landing/{landing_path}...")
    
    paths = landing_fs.get_paths(path=landing_path)
    
    files_processed = 0
    for path in paths:
        if path.name.endswith(".json"):
            print(f"Processing {path.name}...")
            
            # Read JSON file
            file_client = landing_fs.get_file_client(path.name)
            download = file_client.download_file()
            content = download.readall().decode('utf-8')
            
            try:
                data = json.loads(content)
                # The NPPES API returns results in a 'results' key
                if isinstance(data, dict) and 'results' in data:
                    df = pd.json_normalize(data['results'])
                else:
                    df = pd.DataFrame(data)
                
                if df.empty:
                    print(f"Skipping empty file {path.name}")
                    continue
                
                # Add ingestion timestamp
                df['ingestion_timestamp'] = datetime.utcnow()
                df['source_file'] = path.name
                
                # Save to Parquet
                parquet_buffer = io.BytesIO()
                df.to_parquet(parquet_buffer, engine='pyarrow', index=False)
                parquet_data = parquet_buffer.getvalue()
                
                # Create bronze file name (replace .json with .parquet)
                bronze_file_name = path.name.replace("landing/", "").replace(".json", ".parquet")
                bronze_file_client = bronze_fs.get_file_client(f"{bronze_path}/{bronze_file_name}")
                
                print(f"Uploading to bronze/{bronze_path}/{bronze_file_name}...")
                bronze_file_client.create_file()
                bronze_file_client.append_data(data=parquet_data, offset=0, length=len(parquet_data))
                bronze_file_client.flush_data(len(parquet_data))
                
                # Move to processed folder in landing (optional)
                # For now, we'll just leave it or delete it. Let's leave it to keep it simple.
                
                files_processed += 1
                
            except Exception as e:
                print(f"Error processing {path.name}: {e}", file=sys.stderr)

    print(f"Total files processed: {files_processed}")

if __name__ == "__main__":
    storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")
    storage_account_key = os.getenv("STORAGE_ACCOUNT_KEY")
    
    if not storage_account_name or not storage_account_key:
        print("Error: STORAGE_ACCOUNT_NAME and STORAGE_ACCOUNT_KEY must be set.", file=sys.stderr)
        sys.exit(1)
        
    process_npi_landing_to_bronze(storage_account_name, storage_account_key)
