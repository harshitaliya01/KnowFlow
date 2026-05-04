from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from dotenv import load_dotenv
load_dotenv()
import os
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

embedding = OpenAIEmbeddings(
    base_url="https://api.euron.one/api/v1/euri",
    model="text-embedding-3-small"
)
def get_retriever(doc_id):
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embedding,
    )
    return vectorstore.as_retriever(
        search_kwargs={
            "k":3,
            "filter":{
                "must":{"key":"metadata.document_id","match":{"value":str(doc_id)}}
            }
        }
    )