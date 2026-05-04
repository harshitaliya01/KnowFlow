import os
import asyncio
from dotenv import load_dotenv
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance
import logging

logger = logging.getLogger(__name__)

# ✅ Load .env properly (important for nested structure)
from pathlib import Path
# env_path = Path(__file__).resolve().parent / ".env"
# load_dotenv(dotenv_path=env_path)
load_dotenv()
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

VECTOR_SIZE = 1536  # text-embedding-3-small


async def create_collection():
    logger.info(f"🔗 Connecting to: {QDRANT_URL}")

    client = AsyncQdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        # check_compatibility=False
    )

    try:
        # Check if collection exists
        collections = await client.get_collections()
        exists = any(c.name == COLLECTION_NAME for c in collections.collections)

        if exists:
            logger.warning(f"⚠️ Collection '{COLLECTION_NAME}' already exists")
            return

        # Create collection
        await client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            ),
        )

        logger.info(f"✅ Collection '{COLLECTION_NAME}' created successfully")

    except Exception as e:
        logger.exception(f"❌ Error creating collection '{COLLECTION_NAME}'")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(create_collection())


from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType
import os
from dotenv import load_dotenv
load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

client.create_payload_index(
    collection_name=os.getenv("COLLECTION_NAME"),
    field_name="metadata.document_id",   # ⚠️ EXACT SAME PATH
    field_schema=PayloadSchemaType.KEYWORD
)
print("OK all done")

client.close()