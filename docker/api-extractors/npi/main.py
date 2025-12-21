import requests
import pandas as pd
import json
import time
import os
import sys

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
        
        # Simple logging of names found
        for item in results:
            basic = item.get('basic', {})
            name = f"{basic.get('first_name', '')} {basic.get('last_name', '')}"
            print(f"Found Provider: {name} (NPI: {item.get('number')})")
            
        return results
        
    except Exception as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    print("Starting NPI Extractor Job...")
    
    # In a real job, this might run on a schedule or loop.
    # For this test, we run once and exit, or sleep to keep the pod alive for inspection if needed.
    
    data = fetch_npi_data(limit=5)
    
    if data:
        print("Data extraction complete.")
    else:
        print("No data extracted.", file=sys.stderr)
        sys.exit(1)
