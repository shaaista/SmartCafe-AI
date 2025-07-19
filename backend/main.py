import os
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from supabase_client import supabase

# Import route modules
from routes.review_suggestions import router as suggestion_router
from routes.get_reviews import router as recent_reviews_router
from routes.chatbot_reviews import router as chatbot_router
from routes.sentiment import router as sentiment_router
from routes.keywords import router as keywords_router

app = FastAPI()

# CORS - Updated for production with more specific configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://smartcafe-ai.vercel.app",  # Your actual Vercel URL
        "https://*.vercel.app",  # Allow all Vercel preview deployments
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",  # Alternative localhost
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
    ],
)

# Include routers
app.include_router(suggestion_router)
app.include_router(recent_reviews_router)
app.include_router(chatbot_router)
app.include_router(sentiment_router)
app.include_router(keywords_router)

@app.get("/")
async def root():
    return {"message": "SmartCafe AI Backend is running!", "status": "healthy"}

# POST endpoint to submit a review
@app.post("/submit-review")
async def submit_review(
    review_text: str = Form(...),
    rating: int = Form(...)
):
    try:
        # Input validation
        if not review_text or not review_text.strip():
            return {
                "status": "error",
                "message": "Review text cannot be empty"
            }
        
        if rating < 1 or rating > 5:
            return {
                "status": "error", 
                "message": "Rating must be between 1 and 5"
            }
        
        data = {
            "review_text": review_text.strip(),
            "rating": rating,
        }
        
        response = supabase.table("reviews").insert(data).execute()
        
        # Check if the insert was successful
        if response.data:
            return {
                "status": "success",
                "message": "Review submitted successfully.",
                "data": response.data
            }
        else:
            return {
                "status": "error",
                "message": "Failed to save review to database"
            }
            
    except Exception as e:
        print(f"Error in submit_review: {str(e)}")  # Server-side logging
        return {
            "status": "error",
            "message": f"Server error: {str(e)}"
        }
