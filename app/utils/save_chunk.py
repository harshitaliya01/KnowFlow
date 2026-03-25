from app.db.models import Chunk
from app.db.session import AsyncSessionLocal
from fastapi import HTTPException

async def save_chunks(db, chunks): 
        try:
            new_docs = None
            new_docs = [
                Chunk(
                    document_id=int(chunk.metadata.get("document_id")),
                    chunk_id = chunk.metadata.get("chunk_id"),
                    chunk_index=chunk.metadata.get("chunk_index"),
                    content = chunk.page_content,
                    page = chunk.metadata.get("page")
                )
                for chunk in chunks
            ]
            db.add_all(new_docs)
            await db.flush()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")