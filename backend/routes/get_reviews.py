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
        
        # Use 'timestamp' column as shown in your table
        response = supabase.table("reviews").select("*").order("timestamp", desc=True).execute()
        
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
