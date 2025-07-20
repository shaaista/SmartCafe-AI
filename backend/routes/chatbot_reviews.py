import os
from openai import OpenAI
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from supabase_client import supabase
import logging

load_dotenv()

router = APIRouter()
logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    chat_history: Optional[List[ChatMessage]] = []
    coffee_shop_name: Optional[str] = None

async def fetch_recent_reviews():
    """Fetch recent reviews directly from Supabase"""
    try:
        response = supabase.table("reviews").select("review_text, rating, timestamp").order("timestamp", desc=True).limit(30).execute()
        
        if response.data:
            reviews = response.data
            formatted_reviews = []
            for i, review in enumerate(reviews, 1):
                rating_stars = "⭐" * review.get('rating', 0)
                formatted_reviews.append(
                    f"Review #{i}: {rating_stars} ({review.get('rating', 'N/A')}/5)"
                    f"\nDate: {review.get('timestamp', 'Unknown')}"
                    f"\nComment: \"{review.get('review_text', 'No comment')}\"\n---"
                )
            return "\n".join(formatted_reviews[:20])
        return "No reviews found in the database."
    except Exception as e:
        logger.error(f"Error fetching reviews for chatbot: {e}")
        return "Unable to access review data at this time."

@router.post("/chatbot/reviews")
async def chat_with_review_bot(request: ChatRequest):
    """AI business assistant chatbot"""
    try:
        if not OPENROUTER_API_KEY:
            logger.error("OpenRouter API key not configured")
            return {
                "status": "error",
                "answer": "AI assistant is temporarily unavailable. Please check API configuration."
            }

        logger.info(f"Chatbot received question: {request.question}")
        
        # Fetch review data
        reviews_data = await fetch_recent_reviews()
        
        # Improved system prompt for concise responses with context awareness
        system_prompt = f"""You are a concise AI business consultant for {request.coffee_shop_name or 'this coffee shop'}. 

🎯 **RESPONSE STYLE**: Keep responses SHORT (2-3 sentences max) unless asked to elaborate.

📊 **CUSTOMER REVIEWS DATA**:
{reviews_data}

🧠 **CRITICAL CONTEXT RULES**:
1. **FOLLOW-UP COMMANDS** - When user says:
   - "shorten it" / "simplify" → Make your IMMEDIATELY PREVIOUS response 1-2 sentences
   - "elaborate" / "tell me more" → Expand your IMMEDIATELY PREVIOUS response
   - "give details" → Add specifics to your LAST response

2. **CONTEXT AWARENESS**: 
   - Always read the full conversation history before responding
   - Reference your previous answers when user asks for modifications
   - If asked to "shorten" - condense your LAST response, don't give new advice

3. **DEFAULT BEHAVIOR**: 
   - Answer in 2-3 sentences maximum
   - Be direct and actionable
   - Use the review data to support your points

4. **EXAMPLE INTERACTION**:
   User: "What's the best thing about my cafe?"
   You: "Customers love your cute ambiance and friendly staff based on the reviews. The cat sightings are also a unique positive feature customers mention."
   
   User: "shorten it"
   You: "Customers praise your cute ambiance, friendly staff, and the cafe cat."

Remember: Be concise by default, and only expand when specifically asked to elaborate."""

        # Build conversation
        messages = [{"role": "system", "content": system_prompt}]
        
        if request.chat_history:
            recent_history = request.chat_history[-8:]
            for msg in recent_history:
                messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": request.question})

        logger.info("Calling OpenRouter for chatbot response...")

        # Initialize OpenAI client with OpenRouter
        client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

        try:
            response = client.chat.completions.create(
                model="mistralai/mistral-7b-instruct:free",
                messages=messages,
                max_tokens=400,
                temperature=0.6,
                timeout=25
            )
            
            answer = response.choices[0].message.content
            logger.info("Chatbot response generated successfully")
            
            return {"status": "success", "answer": answer}
            
        except Exception as api_error:
            logger.error(f"OpenRouter API error: {api_error}")
            return {
                "status": "error",
                "answer": "I'm having trouble connecting to my AI service right now. Please try again in a moment."
            }
        
    except Exception as e:
        logger.error(f"Chatbot error: {str(e)}")
        return {
            "status": "error",
            "answer": "I apologize, but I encountered an error. Please try asking your question again."
        }
