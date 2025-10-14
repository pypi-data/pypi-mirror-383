import threading
import boto3
from opensearchpy import (
    OpenSearch,
    AWSV4SignerAuth,
    RequestsHttpConnection
)

# from .config.config_loader import env_variable

AWS_PROFILE = "Comm-Prop-Sandbox"
AWS_REGION = "us-east-1"

class OpensearchInstancecreator:
    """singleton approach implemnted for db invoke"""

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def _get_frozen_credentials(self):
        """
        Create AWS session and freeze credentials.
        """
        session = boto3.Session(profile_name=AWS_PROFILE)
        credentials = session.get_credentials()
        return credentials.get_frozen_credentials()

    @classmethod
    def _intialise_os_client(cls, variable_env):
        service = "aoss" #variable_env.SERVICE
        region = "us-east-1" #variable_env.REGION
        host = "mab9oebjshix9m9njfg8.us-east-1.aoss.amazonaws.com" #variable_env.OPENSEARCH_HOST_NAME 
        port = 443 #variable_env.PORT
        credentials = cls._get_frozen_credentials() #boto3.Session().get_credentials() 

        auth = AWSV4SignerAuth(credentials, region, service)
        client = OpenSearch(
            hosts=[{"host": host, "port": int(port)}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            pool_maxsize=20,
        )
        return client

    @classmethod
    def get_os_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls._intialise_os_client(variable_env=None)
                print("connection established: ",cls._instance)
            return cls._instance