from fastapi import HTTPException
from sqlalchemy import select, delete
from app.db.models import User, Document
from app.db.session import get_supabase
from app.services.vector_delete import delete_vectors

async def document_delete(doc_id,db,user):
    try:
        result = await db.execute(select(User).where(User.email == user["email"]))
        current_user = result.scalar_one_or_none()
        print("1")
        if not current_user:
            raise HTTPException(status_code=401, detail="User not found")
        
        result = await db.execute(select(Document).where(Document.id == doc_id))
        document = result.scalar_one_or_none()
        if not document:
            raise HTTPException(status_code=404,detail="Document Not Found")
        print("2")
        
        if document.user_id != current_user.id:
            raise HTTPException(status_code=403,detail="Not Allowed")
        
        
        file_path = document.filepath.split("user-docs/")[-1]
        print(file_path)
        print("3")
        await delete_vectors(doc_id)
        print("6")
        await db.execute(delete(Document).where(Document.id == doc_id))
        await db.commit()
        print("7")
        try:
            print("8")
            supabase = await get_supabase()
            await supabase.storage.from_("user-docs").remove([file_path])
            print("9")
            
        except Exception as e:
            print(str(e))
            raise HTTPException(status_code=500,detail="Internal Server Error1")

    except HTTPException as e:
        print(str(e))
        raise HTTPException(status_code=500,detail=f"Internal Server Error2 {e}")
    
    except Exception as e:
        raise HTTPException(status_code=500,detail="Internal Server Error3")

