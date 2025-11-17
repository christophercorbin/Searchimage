import unittest
from unittest.mock import patch, MagicMock
from clients.db import DbClient
from config import Config

class TestDbClient(unittest.TestCase):
    @patch('boto3.client')
    def setUp(self, mock_boto_client) -> None:
        """Set up test fixtures with mocked AWS calls"""
        self.configs = Config.get("test")

        # Mock the boto3 secrets manager client
        mock_secrets_client = MagicMock()
        mock_boto_client.return_value = mock_secrets_client

        # Mock the secret response
        mock_secrets_client.get_secret_value.return_value = {
            'SecretString': 'mongodb://test:test@localhost:27017/test'
        }

        # Create an instance of DbClient
        self.db_client = DbClient()

    def test_connection_pool_size(self):
        """Test that the pool size configuration is correct"""
        # This test is skipped in CI/CD without real MongoDB
        self.skipTest("Requires MongoDB connection - use integration tests instead")

    def test_singleton_pattern(self):
        """Test that DbClient follows singleton pattern"""
        # Reset singleton for testing
        if hasattr(DbClient, '_instance'):
            DbClient._instance = None

        # Create first instance
        db_client1 = DbClient()
        db_client2 = DbClient()

        # Should be the exact same instance
        self.assertIs(db_client1, db_client2)

    def test_basic_db_operation(self):
        """Test that DbClient is initialized correctly"""
        # Just verify that DbClient can be instantiated without errors
        self.assertIsNotNone(self.db_client)
        self.assertTrue(hasattr(self.db_client, 'get_client'))

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up resources after all tests in this class have run"""
        print("All tests completed, cleaning up resources")
        # Reset the singleton instance
        if hasattr(DbClient, '_instance') and DbClient._instance is not None:
            DbClient._instance = None