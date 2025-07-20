from fastapi import APIRouter, HTTPException
import openai
import os
import logging
from supabase_client import supabase

router = APIRouter()
logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@router.get("/suggestions")
async def get_suggestions():
    """Generate AI suggestions based on recent reviews"""
    try:
        logger.info("Starting suggestions generation...")
        
        if not OPENROUTER_API_KEY:
            logger.error("OpenRouter API key not configured")
            return {"suggestions": "AI suggestions are temporarily unavailable. Please check API key configuration."}
        
        # Fetch recent reviews ordered by timestamp (your actual column name)
        logger.info("Fetching recent reviews for suggestions...")
        response = supabase.table("reviews").select("review_text, rating, timestamp").order("timestamp", desc=True).limit(15).execute()
        
        reviews = response.data if response.data else []
        logger.info(f"Found {len(reviews)} reviews for analysis")
        
        if not reviews:
            return {"suggestions": "No reviews available for analysis yet. Once customers start leaving reviews, I'll provide personalized business suggestions based on their feedback."}

        # Combine reviews with basic format
        combined_reviews = "\n".join([
            f"- \"{r.get('review_text', 'No text')}\" (Rating: {r.get('rating', 'N/A')}/5)" 
            for r in reviews
        ])

        # Simple, focused prompt
        prompt = f"""Based on these {len(reviews)} customer reviews for a coffee shop, provide:

1. Positive Feedback Trends (what customers love)
2. Areas for Improvement (what needs attention)

Reviews:
{combined_reviews}

Keep suggestions practical and actionable."""

        logger.info("Calling OpenRouter API...")
        
        # OpenRouter API call with error handling
        try:
            response = openai.ChatCompletion.create(
                model="mistralai/mistral-7b-instruct:free",
                messages=[
                    {"role": "system", "content": "You are a cafe business consultant providing practical advice based on customer reviews."},
                    {"role": "user", "content": prompt}
                ],
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
                max_tokens=600,
                temperature=0.7,
                timeout=30
            )
            
            suggestions_text = response.choices[0].message["content"]
            logger.info("Successfully generated AI suggestions")
            return {"suggestions": suggestions_text}
            
        except Exception as api_error:
            logger.error(f"OpenRouter API error: {api_error}")
            # Return fallback suggestions based on review data
            return {"suggestions": generate_fallback_suggestions(reviews)}
        
    except Exception as e:
        logger.error(f"Suggestions error: {str(e)}")
        return {"suggestions": f"Unable to generate suggestions: {str(e)}"}

def generate_fallback_suggestions(reviews):
    """Generate basic suggestions if AI API fails"""
    if not reviews:
        return "No review data available for analysis."
    
    total_reviews = len(reviews)
    ratings = [r.get('rating', 0) for r in reviews if r.get('rating')]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    if avg_rating >= 4:
        return f"""Based on {total_reviews} customer reviews:

Positive Feedback Trends:
- Customers are generally satisfied with your service (Average rating: {avg_rating:.1f}/5)
- Good overall rating suggests quality consistency
- Continue emphasizing what customers love most

Areas for Improvement:
- Maintain current quality standards
- Consider expanding successful menu items
- Focus on consistent service delivery"""
    else:
        return f"""Based on {total_reviews} customer reviews:

Areas for Improvement:
- Customer satisfaction could be improved (Average rating: {avg_rating:.1f}/5)
- Review individual feedback for specific issues
- Focus on service quality and consistency

Positive Feedback Trends:
- Identify and strengthen what customers appreciate most
- Build on positive aspects mentioned in reviews"""
