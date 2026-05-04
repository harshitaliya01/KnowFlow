from fastapi import HTTPException, status
from uuid import uuid4
from app.db.session import get_supabase
import asyncio

async def save_document(document):
    try:
        if not hasattr(document, "content_type") or not document.content_type:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content type is missing")

        allowed_types = ["application/pdf", "text/plain"]
        if document.content_type.lower() not in allowed_types:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF and TXT files allowed")
        
        try:
            file_bytes = await document.read()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to read file content")

        if len(file_bytes) > 5 * 1024 * 1024: # 5 MB
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be 5 MB or less")
        
        if document.content_type == "application/pdf" and not file_bytes.startswith(b"%PDF"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid PDF File")
        
        if document.content_type == "application/pdf":
            ext = ".pdf"
        elif document.content_type == "text/plain":
            ext = ".txt"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file format")

        file_path = f"document/{uuid4()}{ext}"
        
        try:
            supabase = await get_supabase()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection error")

        try:
            response = await supabase.storage.from_("user-docs").upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": document.content_type}
            )
            if hasattr(response, "error") and response.error:
                raise Exception(response.error.message)
        except Exception as e:
            print("UPLOAD ERROR:", repr(e), str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload document to storage")
      
        try:
            url_result = supabase.storage.from_("user-docs").get_public_url(file_path)
            if asyncio.iscoroutine(url_result):
                document_url = await url_result
            else:
                document_url = url_result
        except Exception as e:
            print("Get Document URL Error:", repr(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve document URL")
        
        return document_url
    except HTTPException:
        # Re-raise HTTPExceptions so they are handled correctly by FastAPI
        raise
    except Exception as e:
        print("Unexpected Error:", repr(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while saving the document")