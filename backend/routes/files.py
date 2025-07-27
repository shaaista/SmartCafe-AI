from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from supabase import create_client, Client
import os
from datetime import datetime

files_router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase configuration. Please set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@files_router.get("/uploaded-files")
async def get_uploaded_files(cafe_name: str = Query(default="SmartCafe AI")):
    try:
        result = supabase.table('uploaded_files')\
            .select('*')\
            .eq('cafe_name', cafe_name)\
            .order('upload_timestamp', desc=True)\
            .execute()

        formatted_files = []
        for file in result.data:
            size_mb = file['file_size'] / (1024 * 1024)
            upload_date = datetime.fromisoformat(file['upload_timestamp'].replace('Z', '+00:00'))
            formatted_date = upload_date.strftime('%Y-%m-%d')

            formatted_files.append({
                'id': file['id'],
                'name': file['filename'],  # Direct mapping from DB column
                'date': formatted_date,
                'size': f"{size_mb:.1f} MB",
                'status': 'uploaded',
                'supabase_url': file['file_url'],
                'storage_path': file['storage_path']
            })

        return JSONResponse(
            status_code=200,
            content={
                'status': 'success',
                'files': formatted_files
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                'status': 'error',
                'message': f'Failed to retrieve files: {str(e)}',
                'files': []
            }
        )
