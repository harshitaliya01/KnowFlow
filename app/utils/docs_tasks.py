from app.worker.celery_worker import celery_app
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from celery import shared_task
from sqlalchemy import delete
from app.services.document_processor import pdf_to_chunk
from app.services.vector_store import qdrant_vector_store
from app.utils.save_chunk import save_chunks
from app.db.models import Document, Chunk
from app.services.vector_delete import delete_vectors
import os

DB_URL = os.getenv("DATABASE_URL")

@shared_task(bind=True, max_retries=3, soft_time_limit=300)
def process_document(self, file_path, doc_id):
    import asyncio
    async def run():
        engine = create_async_engine(
            DB_URL,
            pool_size=20,
            max_overflow=10,
            pool_recycle=3600,
            connect_args={"ssl":"require","statement_cache_size": 0},
            echo=False,
        )

        AsyncSessionLocal = async_sessionmaker(engine,expire_on_commit=False)
        try:
            async with AsyncSessionLocal() as db:
                document = await db.get(Document, doc_id)
                if not document:
                    return
                if document.status == "Completed":
                    return
                            
            async with AsyncSessionLocal() as db:
                document = await db.get(Document, doc_id)
                if document.status in ["Processing", "Failed"]:
                    await db.execute(delete(Chunk).where(Chunk.document_id == doc_id))
                    await db.commit()
            await delete_vectors(doc_id)
            async with AsyncSessionLocal() as db:
                document = await db.get(Document, doc_id)
                document.status = "Processing"
                await db.commit()

            chunks = await pdf_to_chunk(file_path=file_path, doc_id=doc_id)

                
            await qdrant_vector_store(chunks=chunks)
            async with AsyncSessionLocal() as db:
                await save_chunks(db,chunks)
                document = await db.get(Document, doc_id)
                document.status = "Completed"
                await db.commit()
                
        except Exception as e:
            async with AsyncSessionLocal() as db:
                document = await db.get(Document, doc_id)
                if document:
                    document.status = "Failed"
                    await db.commit()

            raise self.retry(exc=e, countdown=5)
            
    asyncio.run(run())