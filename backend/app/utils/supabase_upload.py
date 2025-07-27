import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_to_supabase(file, bucket_name: str, file_path: str):
    try:
        res = supabase.storage.from_(bucket_name).upload(file_path, file, {"content-type": "text/csv"})
        return res
    except Exception as e:
        return {"error": str(e)}
