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

# CORS - Updated for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://yourapp.vercel.app",  # Replace with your Vercel URL
        "https://*.vercel.app"  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(suggestion_router)
app.include_router(recent_reviews_router)
app.include_router(chatbot_router)
app.include_router(sentiment_router)
app.include_router(keywords_router)

@app.get("/")
async def root():
    return {"message": "SmartCafe AI Backend is running!"}

# Your existing submit-review endpoint...


# POST endpoint to submit a review
@app.post("/submit-review")
async def submit_review(
    review_text: str = Form(...),
    rating: int = Form(...)
):
    try:
        data = {
            "review_text": review_text,
            "rating": rating,
        }
        response = supabase.table("reviews").insert(data).execute()
        return {
            "status": "success",
            "message": "Review submitted successfully.",
            "response": response.data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
