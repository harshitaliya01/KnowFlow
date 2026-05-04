from qdrant_client import QdrantClient
import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()
from langchain_qdrant import QdrantVectorStore
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

embedding = OpenAIEmbeddings(
    base_url="https://api.euron.one/api/v1/euri",
    model="text-embedding-3-small"
)

async def qdrant_vector_store(chunks):
    
    await QdrantVectorStore.afrom_documents(
        documents=chunks,
        embedding=embedding,
        url = os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
        collection_name= COLLECTION_NAME,
    )
    
# def qdrant_vector_store(chunks):
#     QdrantVectorStore.from_documents(
#         documents=chunks,
#         embedding=embedding,
#         url = os.getenv("QDRANT_URL"),
#         # api_key=os.getenv("QDRANT_API_KEY"),
#         collection_name= COLLECTION_NAME,
#     )
