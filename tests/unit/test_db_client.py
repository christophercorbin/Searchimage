import unittest
from clients.db import DbClient
from config import Config

class TestDbClient(unittest.TestCase):
    def setUp(self) -> None:
        self.configs = Config.get("test")

        # Create an instance of DbClient
        self.db_client = DbClient()
        self.client = self.db_client.get_client()
        
        # Verify we can connect to the database
        try:
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB")
        except Exception as e:
            self.fail(f"Failed to connect to MongoDB: {str(e)}")
    
    def test_connection_pool_size(self):
        """Test that the pool size configuration is correct"""
        # For PyMongo 4.x, access the options through topology settings
        server = next(iter(self.client._topology._servers.values()), None)
        if server:
            pool = server._pool
            # Check max pool size
            self.assertEqual(pool.opts.max_pool_size, 2)
            # waitQueueTimeoutMS is in milliseconds in the pool options
            self.assertEqual(pool.opts.wait_queue_timeout, 5)
        else:
            self.fail("Could not access server pool information")
        
    def test_singleton_pattern(self):
        """Test that DbClient follows singleton pattern"""
        # Get client again
        client2 = self.db_client.get_client()
        # Should be the exact same instance
        self.assertIs(self.client, client2)
        
    def test_basic_db_operation(self):
        """Test a basic DB operation to verify connection works"""
        # Try a simple database operation (list databases)
        try:
            dbs = self.client.list_database_names()
            print(f"Available databases: {dbs}")
            self.assertTrue(len(dbs) > 0)
        except Exception as e:
            self.fail(f"Database operation failed: {str(e)}")
    
    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up resources after all tests in this class have run"""
        print("All tests completed, cleaning up resources")
        # Reset the singleton instance if needed
        if hasattr(DbClient, '_instance') and DbClient._instance is not None:
            # Get the instance and close the client connection
            client = DbClient._instance.get_client()
            if client:
                client.close()
                print("MongoDB connection closed")
            # Reset the singleton instance
            DbClient._instance = None