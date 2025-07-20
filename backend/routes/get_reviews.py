from fastapi import APIRouter, HTTPException
from supabase_client import supabase
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/get-reviews")
async def get_reviews():
    """Fetch all reviews from Supabase, ordered by most recent first"""
    try:
        logger.info("Fetching reviews from Supabase...")
        
        # Use created_at if timestamp column doesn't exist, or add both as fallback
        response = supabase.table("reviews").select("*").order("created_at", desc=True).execute()
        
        if response.data is not None:
            logger.info(f"Successfully fetched {len(response.data)} reviews")
            return {
                "status": "success",
                "data": response.data,
                "count": len(response.data)
            }
        else:
            logger.warning("No reviews found in database")
            return {
                "status": "success",
                "data": [],
                "count": 0
            }
            
    except Exception as e:
        logger.error(f"Error fetching reviews: {str(e)}")
        return {
            "status": "error",
            "message": f"Database error: {str(e)}",
            "data": []
        }
