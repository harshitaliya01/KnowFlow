import os
import asyncio
from dotenv import load_dotenv
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance

load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME", "DOCUMENTS")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# 🔥 IMPORTANT: must match your embedding model
VECTOR_SIZE = 1536   # text-embedding-3-small


async def create_collection():
    client = AsyncQdrantClient(url=QDRANT_URL)

    try:
        # Check if collection exists
        collections = await client.get_collections()
        exists = any(c.name == COLLECTION_NAME for c in collections.collections)

        if exists:
            print(f"⚠️ Collection '{COLLECTION_NAME}' already exists")
            return

        # Create collection
        await client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            ),
        )

        print(f"✅ Collection '{COLLECTION_NAME}' created successfully")

    except Exception as e:
        print(f"❌ Error creating collection: {str(e)}")


if __name__ == "__main__":
    asyncio.run(create_collection())