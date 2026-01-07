import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the extractor directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../docker/api-extractors/npi')))

from main import fetch_npi_data

class TestNPIExtractor(unittest.TestCase):

    @patch('main.requests.get')
    def test_fetch_npi_data_success(self, mock_get):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [{'npi': '1234567890', 'basic': {'name': 'Test Doctor'}}]
        }
        mock_get.return_value = mock_response

        results = fetch_npi_data(limit=1)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['npi'], '1234567890')
        mock_get.assert_called_once()

    @patch('main.requests.get')
    def test_fetch_npi_data_failure(self, mock_get):
        # Mock failed response
        mock_get.side_effect = Exception("API Down")

        results = fetch_npi_data(limit=1)
        
        self.assertEqual(results, [])
        mock_get.assert_called_once()

if __name__ == '__main__':
    unittest.main()
