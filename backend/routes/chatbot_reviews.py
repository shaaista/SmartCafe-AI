import os
import openai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from supabase_client import supabase

load_dotenv()

router = APIRouter()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    question: str
    chat_history: Optional[List[ChatMessage]] = []
    coffee_shop_name: Optional[str] = None

async def fetch_recent_reviews():
    """Fetch the 50 most recent reviews directly from Supabase"""
    try:
        response = supabase.table("reviews").select("*").order("timestamp", desc=True).limit(50).execute()
        
        if response.data:
            reviews = response.data
            formatted_reviews = []
            for i, review in enumerate(reviews, 1):
                rating_stars = "⭐" * review.get('rating', 0)
                formatted_reviews.append(
                    f"Review #{i}: {rating_stars} ({review.get('rating', 'N/A')}/5)\n"
                    f"Date: {review.get('timestamp', 'Unknown')}\n"
                    f"Comment: \"{review.get('review_text', 'No comment')}\"\n"
                    f"---"
                )
            return "\n".join(formatted_reviews)
        return "No reviews found in the database."
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        return f"Error accessing review data: {str(e)}"

@router.post("/chatbot/reviews")
async def chat_with_review_bot(request: ChatRequest):
    """Context-aware chatbot for coffee shop business analysis"""
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")

    try:
        print(f"🔥 Received question: {request.question}")
        
        # Fetch actual review data
        reviews_data = await fetch_recent_reviews()
        print(f"📊 Fetched reviews data length: {len(reviews_data)}")
        
        coffee_shop_context = f" for {request.coffee_shop_name}" if request.coffee_shop_name else ""
        
        # Enhanced system prompt
        system_prompt = f"""You are an intelligent AI business consultant for coffee shop owners{coffee_shop_context}.

📊 **ACTUAL CUSTOMER REVIEWS** (Most Recent 50):
{reviews_data}

🧠 **CRITICAL CONVERSATION RULES:**

1. **CONTEXT AWARENESS**: Always read and understand the ENTIRE conversation history before responding.

2. **FOLLOW-UP COMMANDS**: When the user says:
   - "Simplify your response" → Make your IMMEDIATELY PREVIOUS response shorter and simpler
   - "Explain more" → Elaborate on your IMMEDIATELY PREVIOUS response  
   - "Give me one line answer" → Condense your PREVIOUS response to one sentence
   - "Tell me more about that" → Expand on the LAST topic you discussed

3. **REFERENCE ACTUAL DATA**: Use the real customer review data above to answer questions about:
   - Best/worst comments
   - Common complaints
   - Customer praise
   - Areas for improvement

4. **BE CONVERSATIONAL**: Respond like a knowledgeable business partner who remembers everything we've discussed.

🎯 **YOUR EXPERTISE AREAS:**
- Review analysis using actual customer feedback above
- Menu suggestions and trending items
- Business operations and improvements
- Marketing and customer service advice
- Staff and inventory management

Remember: You're having a CONVERSATION with the cafe owner. Each response should connect to what we've been discussing."""

        # Build messages array with conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        if request.chat_history:
            recent_history = request.chat_history[-12:]
            for msg in recent_history:
                messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": request.question})

        print(f"🚀 Calling OpenRouter with {len(messages)} messages")

        # Use OpenRouter API
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=messages,
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
            max_tokens=1500,
            temperature=0.6,
            timeout=30
        )
        
        answer = response["choices"][0]["message"]["content"]
        print(f"✅ OpenRouter responded: {len(answer)} chars")
        
        return {"status": "success", "answer": answer}
        
    except Exception as e:
        print(f"❌ Chatbot error: {str(e)}")
        return {
            "status": "error",
            "answer": "I apologize, but I encountered an error. Please try asking your question again. I can help with menu suggestions, review analysis, business insights, and much more!"
        }
