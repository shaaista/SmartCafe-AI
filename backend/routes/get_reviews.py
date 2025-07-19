from fastapi import APIRouter
from supabase_client import supabase

router = APIRouter()

@router.get("/get-reviews")
async def get_reviews():
    try:
        response = supabase.table("reviews").select("*").order("timestamp", desc=True).execute()
        return {
            "status": "success",
            "data": response.data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
