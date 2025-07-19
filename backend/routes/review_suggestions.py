# routes/review_suggestions.py

from fastapi import APIRouter
from supabase import create_client
import openai
import os

router = APIRouter()

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# OpenRouter config
openai.api_base = "https://openrouter.ai/api/v1"  # OpenRouter endpoint
openai.api_key = os.getenv("OPENROUTER_API_KEY")  # API key

@router.get("/suggestions")
async def get_suggestions():
    # Fetch last 10 reviews
    response = supabase.table("reviews").select("*").order("timestamp", desc=True).limit(10).execute()
    reviews = response.data

    if not reviews:
        return {"suggestions": "No reviews found yet."}

    # Combine reviews
    combined_reviews = "\n".join([f"- {r['review_text']} (Rating: {r['rating']})" for r in reviews])

    # Construct prompt
    prompt = f"""
You are an expert cafe consultant. Based on the following 10 customer reviews, summarize:

1. Positive Feedback Trends
2. Areas for Improvement

Reviews:
{combined_reviews}

Provide your suggestions clearly and concisely.
"""

    # Send request to OpenRouter with Mistral
    completion = openai.ChatCompletion.create(
        model="mistralai/mistral-7b-instruct",
  # ✅ Correct model name on OpenRouter
        messages=[
            {"role": "system", "content": "You are an assistant that analyzes customer reviews for cafes."},
            {"role": "user", "content": prompt}
        ]
    )

    return {"suggestions": completion.choices[0].message["content"]}
