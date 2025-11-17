import threading
import boto3
from botocore.exceptions import ClientError
from pymongo import MongoClient, errors
from config import Config

class DbClient:
    """
    This class is a singleton that's used to create a client connecting to a database.
    """
    _instance = None
    _db_client = None
    _lock = threading.Lock()
    _configs = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DbClient, cls).__new__(cls)
                cls._configs = Config.get()  # Assuming Config.get() is thread-safe and can be called here
        return cls._instance

    def get_client(self):
        if self._db_client is None:
            with self._lock:
                if self._db_client is None:
                    try:
                        self._db_client = self._create_client()
                    except (errors.ConnectionFailure, errors.ServerSelectionTimeoutError) as e:
                        print(f"MongoDB connection failure: {e}")
                        raise

        return self._db_client

    def _create_client(self):
        # get the db secret
        secret = self._get_secret()
        # create the db client with limited pool size and timeouts
        return MongoClient(
            secret,
            maxPoolSize=2,
            waitQueueTimeoutMS=5000,  # Wait at most 5 seconds for a connection from the pool
            serverSelectionTimeoutMS=10000,  # Wait at most 10 seconds for server selection
            socketTimeoutMS=45000  # Socket operations timeout after 45 seconds
        )

    def _get_secret(self):
        secret_name = self._configs.DB_URL_SECRET
        region_name = "us-east-1"

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            # Consider logging the exception here
            print(f'### failed to get secret: {e}')
            raise e

        secret = get_secret_value_response['SecretString']
        return secret
    
    def close(self):
        if self._db_client is not None:
            self._db_client.close()
            self._db_client = None