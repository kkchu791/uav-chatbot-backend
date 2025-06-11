from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from usecases.upload import handle_upload

upload_router = APIRouter()

@upload_router.post("/api/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...)
):
    try:
        session_id = request.cookies.get("session_id")
        if not session_id:
            raise HTTPException(status_code=400, detail="Missing session ID in cookie")

        content = await file.read()
        handle_upload(content, session_id)
        return {"message": "File parsed and stored"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error, {e}")