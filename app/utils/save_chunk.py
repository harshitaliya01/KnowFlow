from app.db.models import Chunk
import traceback

async def save_chunks(db, chunks):
    try:
        new_docs = []
        for chunk in chunks:
            metadata = chunk.metadata or {}

            # ✅ Safe extraction
            document_id = metadata.get("document_id")
            chunk_id = metadata.get("chunk_id")
            chunk_index = metadata.get("chunk_index")
            page_number = metadata.get("page_number", 0)

            # 🚨 Validation (VERY IMPORTANT)
            if document_id is None:
                raise ValueError("document_id missing in metadata")

            new_docs.append(
                Chunk(
                    document_id=int(document_id),
                    chunk_id=str(chunk_id),
                    chunk_index=int(chunk_index) if chunk_index is not None else 0,
                    content=chunk.page_content,
                    page_number=int(page_number)
                )
            )
        new_docs = [
            Chunk(
                document_id=int(chunk.metadata.get("document_id")),
                chunk_id = chunk.metadata.get("chunk_id"),
                chunk_index=chunk.metadata.get("chunk_index"),
                content = chunk.page_content,
                page_number = chunk.metadata.get("page_number")
            )
            for chunk in chunks
        ]
        db.add_all(new_docs)
        await db.flush()
    except Exception as e:
        traceback.print_exc()   # shows actual error
        raise e