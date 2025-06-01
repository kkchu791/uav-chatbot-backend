from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from services.telemetry import store_real_telemetry_in_csv
from services.llm import upload_files_to_llm

upload_router = APIRouter()

@upload_router.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    try:
        content = await file.read()
        store_real_telemetry_in_csv(content)
        upload_files_to_llm(session_id=session_id)
        return {"message": "File parsed and stored", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error, {e}")