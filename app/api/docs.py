from fastapi import APIRouter, UploadFile,Request, File, Depends, Form, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.models import User, Document
from app.db.session import get_db
from app.api.schemas import DocumentOut
from app.utils.get_user import get_current_user
from app.utils.save_doc import save_document
from app.services.rag_pipeline import run_rag
from app.utils.limit import limiter
from app.utils.delete_docs import document_delete
from app.utils.docs_tasks import process_document

router = APIRouter()

@router.get("/health2")
async def health2(user = Depends(get_current_user)):
    return {"health":user}

@router.post("/add/document", response_model=DocumentOut)
@limiter.limit("5/minute")
async def add_document(request: Request, document: UploadFile= File(...),source= Form(...), user = Depends(get_current_user), db: AsyncSession= Depends(get_db)):
    try:
        current_user = await db.execute(select(User).where(User.email == user["email"]))
        current_user = current_user.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")

        document_url = await save_document(document=document)
        new_docs = None
        new_docs = Document(
                user_id=current_user.id,
                filename = document.filename,
                filepath=document_url,
                source = source,
            )
        
        db.add(new_docs)
        await db.commit()
        await db.refresh(new_docs)

        process_document.delay(
            file_path=new_docs.filepath,
            doc_id=new_docs.id
        )

        return {
                "id": new_docs.id,
                "user_id": new_docs.user_id,
                "filename": new_docs.filename,
                "filepath": new_docs.filepath,
                "source": new_docs.source,
                "created_at": str(new_docs.created_at)
        }

    except HTTPException:
        raise

    except Exception as e:
        if new_docs:
            await document_delete(doc_id=new_docs.id,db=db, user=user)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/document/show")
async def document_show(db:AsyncSession= Depends(get_db),user= Depends(get_current_user)):
    try:
        current_user = await db.execute(select(User).where(User.email == user["email"]))
        current_user = current_user.scalar_one_or_none()
        docs = await db.execute(select(Document).where(Document.user_id == current_user.id))
        docs = docs.scalars().all()
        return {
            "docs": [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "filepath": doc.filepath,
                    "status": doc.status,
                    "source": doc.source,
                    "created_at": str(doc.created_at)
                }
                for doc in docs
            ]
        }
        
    except Exception as e:
            raise HTTPException(status_code=500,detail="Internal Server Error")

@router.delete("/document/{doc_id}")
async def delete_document(doc_id:int,db:AsyncSession=Depends(get_db),user= Depends(get_current_user)):
    try:
        await document_delete(doc_id=doc_id,db=db, user=user)
        return {"msg":"Deleted Success"}
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500,detail="Internal Server Error4")

@router.post("/search")
@limiter.limit("5/minute")
async def search_text(request: Request, doc_id: int, query: str, db: AsyncSession= Depends(get_db), user= Depends(get_current_user)):
    current_user = await db.execute(select(User).where(User.email == user["email"]))
    current_user = current_user.scalar_one_or_none()

    document = await db.execute(select(Document).where(Document.id == doc_id))
    document = document.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=400, detail="Document Not Exist Please Reupload The Document")
    if document.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="You Can Not Perform This Action")
    if document.status != "Completed":
        raise HTTPException(status_code=400, detail="Please Re-Upload The Document Or Wait For Processing")
    
    # retriever = get_retriever(doc_id)
    # res = await retriever.ainvoke(query)
    res = await run_rag(query=query, doc_id=doc_id)
    return {"result":res.answer,"page":res.page_number}



@router.get("/document/{doc_id}/status")
async def get_status(doc_id: int, db: AsyncSession = Depends(get_db)):
    doc = await db.get(Document, doc_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "document_id": doc.id,
        "status": doc.status
    }