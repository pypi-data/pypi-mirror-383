#!/usr/bin/env python3
"""
Unit tests for Docuprox
"""

import unittest
import sys
import os
from unittest.mock import patch, mock_open, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from docuprox import Docuprox


class TestDocuprox(unittest.TestCase):

    def setUp(self):
        self.api_key = "test-api-key"
        self.api_url = "https://api.docuprox.com/v1"
        self.client = Docuprox(api_key=self.api_key, api_url=self.api_url)

    def test_init_with_api_key(self):
        client = Docuprox(api_key="test-key")
        self.assertEqual(client.api_key, "test-key")
        self.assertEqual(client.api_url, "https://api.docuprox.com/v1")
        self.assertEqual(client.headers, {'X-auth': 'test-key'})

    def test_init_without_api_key_raises_error(self):
        with self.assertRaises(ValueError):
            Docuprox()

    def test_init_with_env_vars(self):
        with patch.dict(os.environ, {'DOCUPROX_API_KEY': 'env-key', 'DOCUPROX_API_URL': 'http://env-url.com'}):
            client = Docuprox()
            self.assertEqual(client.api_key, 'env-key')
            self.assertEqual(client.api_url, 'http://env-url.com')

    @patch('requests.post')
    def test_processbase64_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'result': 'success'}
        mock_post.return_value = mock_response

        result = self.client.processbase64("SGVsbG8=", "template-123")
        self.assertEqual(result, {'result': 'success'})
        mock_post.assert_called_once_with(
            f"{self.api_url}/process",
            json={"actual_image": "SGVsbG8=", "template_id": "template-123"},
            headers=self.client.headers
        )

    @patch('requests.post')
    def test_processbase64_api_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_response.json.return_value = {'error': 'Invalid request'}
        mock_post.return_value = mock_response

        with self.assertRaises(Exception):  # The exception is raised before ValueError
            self.client.processbase64("SGVsbG8=", "template-123")

    @patch('builtins.open', new_callable=mock_open, read_data=b'file content')
    @patch('requests.post')
    def test_processfile_success(self, mock_post, mock_file):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'result': 'success'}
        mock_post.return_value = mock_response

        result = self.client.processfile("test.pdf", "template-123")
        self.assertEqual(result, {'result': 'success'})

        # Verify file was opened correctly
        mock_file.assert_called_once_with("test.pdf", 'rb')

        # Verify the multipart request was made
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], f"{self.api_url}/process")
        self.assertIn('files', call_args[1])
        self.assertIn('data', call_args[1])
        self.assertEqual(call_args[1]['data']['template_id'], 'template-123')

    def test_processfile_file_not_found(self):
        with self.assertRaises(ValueError):
            self.client.processfile("nonexistent.pdf", "template-123")


if __name__ == '__main__':
    unittest.main()
