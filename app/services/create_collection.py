import os
import asyncio
from dotenv import load_dotenv
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance

# ✅ Load .env properly (important for nested structure)
from pathlib import Path
# env_path = Path(__file__).resolve().parent / ".env"
# load_dotenv(dotenv_path=env_path)
load_dotenv()
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "DOCUMENTS")
QDRANT_URL = os.getenv("QDRANT_URL")
# QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

VECTOR_SIZE = 1536  # text-embedding-3-small


async def create_collection():
    print("🔗 Connecting to:", QDRANT_URL)

    client = AsyncQdrantClient(
        url=QDRANT_URL,
        # api_key=QDRANT_API_KEY,
        # check_compatibility=False
    )

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
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(create_collection())