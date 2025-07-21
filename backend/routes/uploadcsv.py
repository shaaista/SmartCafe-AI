from flask import Blueprint, request, jsonify
from supabase import create_client, Client
import os
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
import tempfile

# Create Blueprint
uploadcsv_bp = Blueprint('uploadcsv', __name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for uploads

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase configuration. Please set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables.")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuration
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file):
    """Check if file size is within limits"""
    file.seek(0, 2)  # Seek to end of file
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    return file_size <= MAX_FILE_SIZE

@uploadcsv_bp.route('/upload-csv', methods=['POST'])
def upload_csv():
    """
    Upload CSV file to Supabase Storage
    Expected form data:
    - csv_file: The CSV file to upload
    - cafe_name: Name of the cafe (optional, for organization)
    """
    try:
        # Check if file is in request
        if 'csv_file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file provided'
            }), 400

        file = request.files['csv_file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400

        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': 'Only CSV files are allowed'
            }), 400

        # Validate file size
        if not validate_file_size(file):
            return jsonify({
                'status': 'error',
                'message': f'File size exceeds {MAX_FILE_SIZE/1024/1024}MB limit'
            }), 400

        # Get additional parameters
        cafe_name = request.form.get('cafe_name', 'default_cafe')
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{cafe_name}_{timestamp}_{unique_id}_{original_filename}"

        # Create temporary file to read content
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            file.save(tmp_file.name)
            
            # Read file content
            with open(tmp_file.name, 'rb') as f:
                file_content = f.read()

            # Upload to Supabase Storage
            # You'll need to create a bucket called 'csv-uploads' in your Supabase dashboard
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

            # Clean up temp file
            os.unlink(tmp_file.name)

            # Check if upload was successful
            if hasattr(result, 'error') and result.error:
                return jsonify({
                    'status': 'error',
                    'message': f'Upload failed: {result.error.message}'
                }), 500

            # Get public URL
            file_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)

            # Store file metadata in database (optional)
            # Create a table called 'uploaded_files' in your Supabase database
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

            return jsonify({
                'status': 'success',
                'message': 'File uploaded successfully',
                'file_url': file_url,
                'filename': filename,
                'storage_path': storage_path,
                'file_id': db_result.data[0]['id'] if db_result.data else None,
                'file_size': len(file_content)
            }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Upload failed: {str(e)}'
        }), 500

@uploadcsv_bp.route('/uploaded-files', methods=['GET'])
def get_uploaded_files():
    """Get list of uploaded files for a cafe"""
    try:
        cafe_name = request.args.get('cafe_name', 'default_cafe')
        
        # Query uploaded files from database
        result = supabase.table('uploaded_files')\
            .select('*')\
            .eq('cafe_name', cafe_name)\
            .order('upload_timestamp', desc=True)\
            .execute()

        return jsonify({
            'status': 'success',
            'files': result.data
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve files: {str(e)}'
        }), 500

@uploadcsv_bp.route('/delete-file/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a file from Supabase Storage and database"""
    try:
        # Get file info from database
        result = supabase.table('uploaded_files')\
            .select('*')\
            .eq('id', file_id)\
            .execute()

        if not result.data:
            return jsonify({
                'status': 'error',
                'message': 'File not found'
            }), 404

        file_info = result.data[0]
        bucket_name = 'csv-uploads'
        
        # Delete from Supabase Storage
        storage_result = supabase.storage.from_(bucket_name).remove([file_info['storage_path']])
        
        # Delete from database
        supabase.table('uploaded_files').delete().eq('id', file_id).execute()

        return jsonify({
            'status': 'success',
            'message': 'File deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to delete file: {str(e)}'
        }), 500
