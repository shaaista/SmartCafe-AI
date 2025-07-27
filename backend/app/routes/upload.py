from fastapi import APIRouter, UploadFile, File
from app.utils.supabase_upload import upload_to_supabase

router = APIRouter()

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    contents = await file.read()
    bucket_name = "csv-uploads"  # 👈 Create this bucket in Supabase UI
    file_path = f"raw/{file.filename}"

    response = upload_to_supabase(contents, bucket_name, file_path)
    return {"status": "success", "details": response}
