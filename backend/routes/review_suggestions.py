from fastapi import APIRouter, HTTPException
from openai import OpenAI
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
        logger.info("=== Starting AI Suggestions Generation ===")
        
        if not OPENROUTER_API_KEY:
            logger.error("❌ OpenRouter API key not found")
            return {"suggestions": "AI suggestions are temporarily unavailable. API key not configured."}
        
        logger.info("✅ OpenRouter API key found")
        
        # Fetch recent reviews from Supabase
        logger.info("📊 Fetching reviews from Supabase...")
        try:
            response = supabase.table("reviews").select("review_text, rating, timestamp").order("timestamp", desc=True).limit(10).execute()
            reviews = response.data if response.data else []
            logger.info(f"✅ Fetched {len(reviews)} reviews successfully")
        except Exception as db_error:
            logger.error(f"❌ Database error: {db_error}")
            return {"suggestions": f"Database connection failed: {str(db_error)}"}
        
        if not reviews:
            logger.info("ℹ️ No reviews found")
            return {"suggestions": "No reviews available for analysis yet. Once customers start leaving reviews, I'll provide personalized business suggestions based on their feedback."}

        # Format reviews for AI
        review_text = "\n".join([
            f"Review: \"{r.get('review_text', '')}\" | Rating: {r.get('rating', 0)}/5"
            for r in reviews
        ])

        logger.info(f"📝 Formatted {len(reviews)} reviews for AI analysis")

        # Create the prompt
        prompt = f"""You are a business consultant for a coffee shop. Analyze these customer reviews and provide actionable suggestions:

{review_text}

Please provide:
1. What customers love (positive trends)
2. Areas that need improvement
3. Specific actionable recommendations

Keep it concise and practical."""

        logger.info("🤖 Calling OpenRouter API...")

        # Initialize OpenAI client with OpenRouter configuration
        client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

        try:
            response = client.chat.completions.create(
                model="mistralai/mistral-7b-instruct:free",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful business consultant specializing in coffee shops and restaurants."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7,
                timeout=30
            )
            
            suggestion_text = response.choices[0].message.content
            logger.info(f"✅ AI suggestions generated successfully ({len(suggestion_text)} chars)")
            return {"suggestions": suggestion_text}
                
        except Exception as api_error:
            logger.error(f"❌ OpenRouter API error: {api_error}")
            return {"suggestions": generate_fallback_suggestions(reviews)}
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in suggestions: {str(e)}")
        return {"suggestions": f"Service temporarily unavailable: {str(e)}"}

def generate_fallback_suggestions(reviews):
    """Generate basic suggestions when AI API fails"""
    if not reviews:
        return "No review data available for analysis."
    
    total_reviews = len(reviews)
    ratings = [r.get('rating', 0) for r in reviews if r.get('rating')]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Analyze rating distribution
    high_ratings = sum(1 for r in ratings if r >= 4)
    low_ratings = sum(1 for r in ratings if r <= 2)
    
    suggestions = f"""📊 **Analysis of {total_reviews} Recent Reviews**

**Overall Performance:**
- Average Rating: {avg_rating:.1f}/5
- Positive Reviews (4-5 stars): {high_ratings}
- Negative Reviews (1-2 stars): {low_ratings}

**Positive Feedback Trends:**
"""
    
    if avg_rating >= 4.0:
        suggestions += "- Customers are generally very satisfied with your service\n- Maintain your current quality standards\n- Consider expanding what's working well\n"
    elif avg_rating >= 3.0:
        suggestions += "- Some customers appreciate your offerings\n- There's room for improvement in service delivery\n- Focus on consistency\n"
    else:
        suggestions += "- Limited positive feedback in recent reviews\n- Immediate attention needed for service quality\n- Consider customer service training\n"
    
    suggestions += "\n**Areas for Improvement:**\n"
    
    if low_ratings > high_ratings:
        suggestions += "- Address customer complaints promptly\n- Review service procedures\n- Train staff on customer service excellence\n"
    elif avg_rating < 4.0:
        suggestions += "- Focus on exceeding customer expectations\n- Improve consistency in service delivery\n- Consider menu quality and variety\n"
    else:
        suggestions += "- Continue current practices\n- Look for opportunities to innovate\n- Maintain staff training programs\n"
    
    return suggestions
