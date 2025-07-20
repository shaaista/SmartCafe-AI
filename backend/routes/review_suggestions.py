from fastapi import APIRouter, HTTPException
import openai
import os
import logging
from supabase_client import supabase

router = APIRouter()
logger = logging.getLogger(__name__)

# OpenRouter config
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@router.get("/suggestions")
async def get_suggestions():
    """Generate AI suggestions based on recent reviews"""
    try:
        if not OPENROUTER_API_KEY:
            logger.error("OpenRouter API key not configured")
            return {"suggestions": "AI suggestions are temporarily unavailable. API key not configured."}
        
        # Fetch last 20 reviews from Supabase
        logger.info("Fetching recent reviews for suggestions...")
        response = supabase.table("reviews").select("*").order("created_at", desc=True).limit(20).execute()
        
        reviews = response.data if response.data else []
        
        if not reviews:
            return {"suggestions": "No reviews found yet. Once customers start leaving reviews, I'll provide personalized business suggestions based on their feedback."}

        # Combine reviews
        combined_reviews = "\n".join([
            f"- {r.get('review_text', 'No text')} (Rating: {r.get('rating', 'N/A')}/5)" 
            for r in reviews
        ])

        # Construct prompt
        prompt = f"""
You are an expert cafe business consultant. Based on the following {len(reviews)} customer reviews, provide:

1. **Positive Feedback Trends** - What customers are praising
2. **Areas for Improvement** - What needs attention

Customer Reviews:
{combined_reviews}

Provide actionable business suggestions in a clear, professional format.
"""

        # Send request to OpenRouter with Mistral
        logger.info("Calling OpenRouter API for suggestions...")
        completion = openai.ChatCompletion.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[
                {"role": "system", "content": "You are a business consultant that analyzes customer reviews for cafes and provides actionable insights."},
                {"role": "user", "content": prompt}
            ],
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
            max_tokens=800,
            temperature=0.7
        )

        suggestions_text = completion.choices[0].message["content"]
        logger.info(f"Generated suggestions: {len(suggestions_text)} characters")
        
        return {"suggestions": suggestions_text}
        
    except Exception as e:
        logger.error(f"Suggestions error: {str(e)}")
        return {"suggestions": f"Unable to generate suggestions at this time. Error: {str(e)}"}
