from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from supabase import create_client, Client
import os
from datetime import datetime
import uuid
import re
import unicodedata

# Custom secure_filename function to replace werkzeug dependency
def secure_filename(filename: str) -> str:
    """Pass it a filename and it will return a secure version of it."""
    if not filename:
        return "unknown"
    
    # Normalize unicode characters to ASCII
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    
    # Replace unsafe characters with underscores
    filename = re.sub(r'[^A-Za-z0-9_.-]', '_', filename)
    
    # Remove multiple consecutive underscores/dots/dashes
    filename = re.sub(r'[_.-]+', lambda m: m.group(0)[0], filename)
    
    # Remove leading/trailing dots and underscores
    filename = filename.strip('._')
    
    # Ensure we have a filename
    if not filename:
        return "unknown"
    
    return filename

# Create router instead of Blueprint
uploadcsv_router = APIRouter()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase configuration. Please set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables.")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuration
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@uploadcsv_router.post("/upload-csv")
async def upload_csv(
    csv_file: UploadFile = File(...),
    cafe_name: str = Form(default="default_cafe")
):
    """Upload CSV file to Supabase Storage"""
    try:
        # Validate file type
        if not allowed_file(csv_file.filename):
            return JSONResponse(
                status_code=400,
                content={
                    'status': 'error',
                    'message': 'Only CSV files are allowed'
                }
            )

        # Read file content
        file_content = await csv_file.read()
        
        # Validate file size
        if len(file_content) > MAX_FILE_SIZE:
            return JSONResponse(
                status_code=400,
                content={
                    'status': 'error',
                    'message': f'File size exceeds {MAX_FILE_SIZE/1024/1024}MB limit'
                }
            )

        # Generate unique filename using custom secure_filename function
        original_filename = secure_filename(csv_file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{cafe_name}_{timestamp}_{unique_id}_{original_filename}"

        # Upload to Supabase Storage
        bucket_name = 'csv-uploads'
        storage_path = f"orders/{filename}"

        # Upload file to Supabase Storage
        result = supabase.storage.from_(bucket_name).upload(
            path=storage_path,
            file=file_content,
            file_options={
                "content-type": "text/csv",
                "upsert": False
            }
        )

        # Check if upload was successful
        if hasattr(result, 'error') and result.error:
            return JSONResponse(
                status_code=500,
                content={
                    'status': 'error',
                    'message': f'Upload failed: {result.error.message}'
                }
            )

        # Get public URL
        file_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)

        # Store file metadata in database
        file_metadata = {
            'filename': original_filename,
            'storage_path': storage_path,
            'file_url': file_url,
            'cafe_name': cafe_name,
            'file_size': len(file_content),
            'upload_timestamp': datetime.now().isoformat(),
            'file_type': 'csv'
        }

        # Insert metadata into database
        db_result = supabase.table('uploaded_files').insert(file_metadata).execute()

        return JSONResponse(
            status_code=200,
            content={
                'status': 'success',
                'message': 'File uploaded successfully',
                'file_url': file_url,
                'filename': filename,
                'storage_path': storage_path,
                'file_id': db_result.data[0]['id'] if db_result.data else None,
                'file_size': len(file_content)
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                'status': 'error',
                'message': f'Upload failed: {str(e)}'
            }
        )

@uploadcsv_router.get("/uploaded-files")
async def get_uploaded_files(cafe_name: str = "default_cafe"):
    """Get list of uploaded files for a cafe"""
    try:
        # Query uploaded files from database
        result = supabase.table('uploaded_files')\
            .select('*')\
            .eq('cafe_name', cafe_name)\
            .order('upload_timestamp', desc=True)\
            .execute()

        return JSONResponse(
            status_code=200,
            content={
                'status': 'success',
                'files': result.data
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                'status': 'error',
                'message': f'Failed to retrieve files: {str(e)}'
            }
        )

@uploadcsv_router.delete("/delete-file/{file_id}")
async def delete_file(file_id: int):
    """Delete a file from Supabase Storage and database"""
    try:
        # Get file info from database
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
