from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from supabase import create_client, Client
import os

# Create router
files_router = APIRouter()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase configuration. Please set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables.")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@files_router.get("/uploaded-files")
async def get_uploaded_files(cafe_name: str = Query(default="SmartCafe AI")):
    """Get list of uploaded files for a cafe"""
    try:
        # Query uploaded files from database
        result = supabase.table('uploaded_files')\
            .select('*')\
            .eq('cafe_name', cafe_name)\
            .order('upload_timestamp', desc=True)\
            .execute()

        # Format the files for frontend display
        formatted_files = []
        for file in result.data:
            # Convert bytes to MB for display
            size_mb = file['file_size'] / (1024 * 1024)
            
            # Format date from ISO to readable format
            from datetime import datetime
            upload_date = datetime.fromisoformat(file['upload_timestamp'].replace('Z', '+00:00'))
            formatted_date = upload_date.strftime('%Y-%m-%d')
            
            formatted_files.append({
                'id': file['id'],
                'name': file['filename'],
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

@files_router.delete("/delete-file/{file_id}")
async def delete_uploaded_file(file_id: int):
    """Delete a file from both Supabase Storage and database"""
    try:
        # Get file info from database first
        result = supabase.table('uploaded_files')\
            .select('*')\
            .eq('id', file_id)\
            .execute()

        if not result.data:
            return JSONResponse(
                status_code=404,
                content={
                    'status': 'error',
                    'message': 'File not found'
                }
            )

        file_info = result.data[0]
        bucket_name = 'csv-uploads'
        
        # Delete from Supabase Storage
        storage_result = supabase.storage.from_(bucket_name).remove([file_info['storage_path']])
        
        # Delete from database
        supabase.table('uploaded_files').delete().eq('id', file_id).execute()

        return JSONResponse(
            status_code=200,
            content={
                'status': 'success',
                'message': 'File deleted successfully'
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                'status': 'error',
                'message': f'Failed to delete file: {str(e)}'
            }
        )
