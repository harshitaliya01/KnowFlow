from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import os

async def delete_vectors(doc_id: int):
    collection = os.getenv("COLLECTION_NAME")
    client = AsyncQdrantClient(
        url=os.getenv("QDRANT_URL"),
        # api_key=os.getenv("QDRANT_API_KEY"),
    )

    search_result = await client.scroll(
        collection_name=collection,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=str(doc_id))
                )
            ]
        ),
        limit=1,
        with_payload=False, 
        with_vectors=False
    )
    points = search_result[0]

    if points:
        await client.delete(
            collection_name=collection,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=str(doc_id))
                    )
                ]
            )
        )
    else:
        pass