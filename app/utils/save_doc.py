from fastapi import HTTPException
from uuid import uuid4
from app.db.session import get_supabase

async def save_document(document):
    if not document.content_type.lower().startswith("application/pdf"):
        raise HTTPException(status_code=400, detail="Only Pdf File Allowed")
    file_bytes = await document.read()
    max_size = 5 * 1024 * 1024 

    if len(file_bytes) > max_size:
        raise HTTPException(status_code=400, detail="PDF must be 5 MB or less")
    
    if not file_bytes.startswith(b"%PDF"):
        raise HTTPException(status_code=400,detail="Invalid PDF File")
    
    file_path = f"document/{uuid4()}.pdf"
    supabase = await get_supabase()
    try:
        await supabase.storage.from_("user-docs").upload(
            file_path,file_bytes, {"content-type": "application/pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Document Not Upload")

    try:
        document_url = await supabase.storage.from_("user-docs").get_public_url(file_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Get Document Error")
    
    return document_url