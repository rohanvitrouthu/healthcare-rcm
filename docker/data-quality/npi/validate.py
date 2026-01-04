import os
import sys
import pandas as pd
import great_expectations as ge
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core.exceptions import AzureError
import io

def get_service_client(storage_account_name, storage_account_key):
    return DataLakeServiceClient(
        account_url=f"https://{storage_account_name}.dfs.core.windows.net",
        credential=storage_account_key
    )

def validate_bronze_npi(storage_account_name, storage_account_key):
    service_client = get_service_client(storage_account_name, storage_account_key)
    bronze_fs = service_client.get_file_system_client(file_system="bronze")
    
    bronze_path = "npi_data"
    print(f"Checking for files in bronze/{bronze_path} for validation...")
    
    paths = bronze_fs.get_paths(path=bronze_path)
    
    for path in paths:
        if path.name.endswith(".parquet"):
            print(f"Validating {path.name}...")
            
            # Read Parquet file
            file_client = bronze_fs.get_file_client(path.name)
            download = file_client.download_file()
            content = download.readall()
            
            df = pd.read_parquet(io.BytesIO(content))
            
            # Wrap with Great Expectations
            ge_df = ge.from_pandas(df)
            
            # Expectations
            print("Running expectations...")
            
            # 1. NPI should not be null
            results_npi_not_null = ge_df.expect_column_values_to_not_be_null("number")
            
            # 2. NPI should be a certain length (it's often returned as int or string of 10 digits)
            # NPPES returns it as integer in JSON usually, but let's check
            # ge_df.expect_column_value_lengths_to_equal("number", 10) # If it's a string
            
            # 3. Basic info should exist
            results_first_name = ge_df.expect_column_to_exist("basic.first_name")
            results_last_name = ge_df.expect_column_to_exist("basic.last_name")
            
            if results_npi_not_null["success"] and results_first_name["success"]:
                print(f"Validation SUCCESS for {path.name}")
            else:
                print(f"Validation FAILURE for {path.name}")
                print(f"Results: {json.dumps(results_npi_not_null, indent=2)}")
                # In a real pipeline, we might move the file to a 'quarantine' folder or alert.

if __name__ == "__main__":
    storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")
    storage_account_key = os.getenv("STORAGE_ACCOUNT_KEY")
    
    if not storage_account_name or not storage_account_key:
        print("Error: STORAGE_ACCOUNT_NAME and STORAGE_ACCOUNT_KEY must be set.", file=sys.stderr)
        sys.exit(1)
        
    validate_bronze_npi(storage_account_name, storage_account_key)
