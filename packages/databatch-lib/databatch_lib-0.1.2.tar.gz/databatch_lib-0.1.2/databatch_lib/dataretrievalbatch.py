from databatch_lib.db_instances_ import OpensearchInstancecreator
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
import numpy as np
import json

os_client = OpensearchInstancecreator().get_os_instance()
index_name = "test_index"


def searchby_text(query_text: str):
    """Search documents using text match."""
    search_body = {"query": {"match": {"content": query_text}}}

    res = os_client.search(index=index_name, body=search_body)
    for hit in res["hits"]["hits"]:
        print(hit["_source"]["title"], "→", hit["_score"])


def searchby_embedding():
    """Vector search using cosine similarity (if supported)."""
    query_embedding = np.random.rand(1536).tolist()

    vector_query = {
        "size": 2,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_embedding},
                },
            }
        },
    }

    try:
        res = os_client.search(index=index_name, body=vector_query)
        for hit in res["hits"]["hits"]:
            print(hit["_source"]["title"], "→", hit["_score"])
    except Exception as e:
        print("⚠️ Vector search not supported in this cluster.")
        print("Error:", e)
