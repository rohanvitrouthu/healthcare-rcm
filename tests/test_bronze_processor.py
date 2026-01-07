import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import pandas as pd
import io

# Add the processor directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../docker/bronze-processor/npi')))

from main import process_npi_landing_to_bronze

class TestBronzeProcessor(unittest.TestCase):

    @patch('main.get_service_client')
    def test_process_npi_landing_to_bronze(self, mock_get_client):
        # Mock Azure Service Client and File System Clients
        mock_client = MagicMock()
        mock_landing_fs = MagicMock()
        mock_bronze_fs = MagicMock()
        
        mock_get_client.return_value = mock_client
        mock_client.get_file_system_client.side_effect = lambda file_system: \
            mock_landing_fs if file_system == "landing" else mock_bronze_fs

        # Mock path list
        mock_path = MagicMock()
        mock_path.name = "npi_data/test.json"
        mock_landing_fs.get_paths.return_value = [mock_path]

        # Mock file download
        mock_file_client = MagicMock()
        mock_landing_fs.get_file_client.return_value = mock_file_client
        mock_download = MagicMock()
        mock_download.readall.return_value = b'{"results": [{"npi": "123"}]}'
        mock_file_client.download_file.return_value = mock_download

        # Mock bronze file upload
        mock_bronze_file_client = MagicMock()
        mock_bronze_fs.get_file_client.return_value = mock_bronze_file_client

        process_npi_landing_to_bronze("test_acc", "test_key")

        # Verify interactions
        mock_landing_fs.get_paths.assert_called_once()
        mock_landing_fs.get_file_client.assert_called_with("npi_data/test.json")
        mock_bronze_fs.get_file_client.assert_called()
        mock_bronze_file_client.create_file.assert_called_once()

if __name__ == '__main__':
    unittest.main()
