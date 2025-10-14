from databatch_lib.db_instances_ import OpensearchInstancecreator
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
import numpy as np
import json

os_client = OpensearchInstancecreator().get_os_instance()
index_name = "test_index"


def create_index():
    """Creates an index, handles dense_vector incompatibility automatically."""
    index_body = {
        "settings": {"number_of_shards": 1, "number_of_replicas": 0},
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "content": {"type": "text"},
                # We will try dense_vector, and fallback if unsupported
                "embedding": {"type": "dense_vector", "dims": 1536}
            }
        },
    }

    if os_client.indices.exists(index=index_name):
        print(f"Index '{index_name}' already exists")
        return

    try:
        os_client.indices.create(index=index_name, body=index_body)
        print(f"✅ Created index '{index_name}' with dense_vector mapping")
    except Exception as e:
        if "dense_vector" in str(e):
            print("⚠️ dense_vector not supported. Creating index without vector field.")
            del index_body["mappings"]["properties"]["embedding"]
            os_client.indices.create(index=index_name, body=index_body)
            print(f"✅ Created index '{index_name}' (without embedding field)")
        else:
            raise


def insert_docs():
    """Insert example documents."""
    docs = [
        {
            "_index": index_name,
            "_source": {
                "title": "OpenSearch Introduction",
                "content": "OpenSearch is a distributed search engine.",
                "embedding": np.random.rand(1536).tolist(),
            },
        },
        {
            "_index": index_name,
            "_source": {
                "title": "Vector Search Example",
                "content": "You can search documents by semantic vectors.",
                "embedding": np.random.rand(1536).tolist(),
            },
        },
    ]

    success, failed = bulk(os_client, docs, raise_on_error=False)
    print(f"Inserted {success} docs, failed: {failed}")

