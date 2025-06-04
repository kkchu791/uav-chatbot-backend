from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from usecases.upload import handle_upload


upload_router = APIRouter()

@upload_router.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    try:
        content = await file.read()
        handle_upload(content, session_id)
        return {"message": "File parsed and stored", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error, {e}")