import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase_client import supabase
import logging

# Import route modules
from routes.review_suggestions import router as suggestion_router
from routes.get_reviews import router as recent_reviews_router
from routes.chatbot_reviews import router as chatbot_router
from routes.sentiment import router as sentiment_router
from routes.keywords import router as keywords_router
from routes.uploadcsv import uploadcsv_router

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SmartCafe AI Backend",
    description="AI-powered cafe management dashboard backend",
    version="1.0.0"
)

# CORS - Updated for production with more specific configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "http://localhost:5173",  # Vite dev server
        "https://smart-cafe-ai.vercel.app",  # Your ACTUAL Vercel URL (with hyphen)
        "https://smartcafe-ai.vercel.app",   # Keep the old one just in case
        "https://*.vercel.app"  # Allow all Vercel deployments
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "X-CSRF-Token",
    ],
)

# Include routers
app.include_router(suggestion_router)
app.include_router(recent_reviews_router)
app.include_router(chatbot_router)
app.include_router(sentiment_router)
app.include_router(keywords_router)
app.include_router(uploadcsv_router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "SmartCafe AI Backend is running!", "status": "healthy", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Detailed health check with database connection test"""
    try:
        # Test database connection
        response = supabase.table("reviews").select("count", count="exact").limit(1).execute()
        return {
            "status": "healthy",
            "database": "connected",
            "message": "All systems operational",
            "review_count": response.count if hasattr(response, 'count') else 0
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy", 
            "database": "disconnected",
            "error": str(e),
            "message": "Database connection failed"
        }

# POST endpoint to submit a review
@app.post("/submit-review")
async def submit_review(
    review_text: str = Form(...),
    rating: int = Form(...)
):
    """Submit a new customer review"""
    try:
        # Input validation
        if not review_text or not review_text.strip():
            logger.warning("Empty review text submitted")
            return {
                "status": "error",
                "message": "Review text cannot be empty"
            }
        
        if rating < 1 or rating > 5:
            logger.warning(f"Invalid rating submitted: {rating}")
            return {
                "status": "error", 
                "message": "Rating must be between 1 and 5"
            }
        
        # Prepare data for insertion
        data = {
            "review_text": review_text.strip(),
            "rating": rating,
        }
        
        logger.info(f"Attempting to insert review with rating: {rating}")
        
        # Insert into Supabase
        response = supabase.table("reviews").insert(data).execute()
        
        # Check if the insert was successful
        if response.data and len(response.data) > 0:
            logger.info(f"Review inserted successfully: {response.data[0]}")
            return {
                "status": "success",
                "message": "Review submitted successfully.",
                "data": response.data[0]
            }
        else:
            logger.error(f"Insert response was empty or invalid: {response}")
            return {
                "status": "error",
                "message": "Failed to save review to database"
            }
            
    except Exception as e:
        logger.error(f"Error in submit_review: {str(e)}")
        return {
            "status": "error",
            "message": f"Server error: {str(e)}"
        }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"status": "error", "message": "Endpoint not found", "detail": str(exc)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {"status": "error", "message": "Internal server error", "detail": str(exc)}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("SmartCafe AI Backend starting up...")
    
    # Test database connection on startup
    try:
        response = supabase.table("reviews").select("count", count="exact").limit(1).execute()
        logger.info("✅ Database connection successful on startup")
    except Exception as e:
        logger.error(f"❌ Database connection failed on startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("SmartCafe AI Backend shutting down...")
