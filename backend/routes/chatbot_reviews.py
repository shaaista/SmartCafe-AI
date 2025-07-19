import os
import openai
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

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
    """Fetch the 50 most recent reviews from the database"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://127.0.0.1:8000/get-reviews")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and data.get("data"):
                    reviews = data["data"][:50]
                    
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
            return "Unable to fetch reviews from the database."
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        return f"Error accessing review data: {str(e)}"

@router.post("/chatbot/reviews")
async def chat_with_review_bot(request: ChatRequest):
    """
    Context-aware chatbot for coffee shop business analysis
    """
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")

    try:
        print(f"🔥 Received question: {request.question}")
        
        # Fetch actual review data
        reviews_data = await fetch_recent_reviews()
        print(f"📊 Fetched reviews data length: {len(reviews_data)}")
        
        coffee_shop_context = f" for {request.coffee_shop_name}" if request.coffee_shop_name else ""
        
        # ENHANCED SYSTEM PROMPT FOR PERFECT CONTEXT UNDERSTANDING
        system_prompt = f"""You are an intelligent AI business consultant for coffee shop owners{coffee_shop_context}. You MUST maintain perfect conversational context like a human consultant would.

📊 **ACTUAL CUSTOMER REVIEWS** (Most Recent 50):
{reviews_data}

🧠 **CRITICAL CONVERSATION RULES - FOLLOW EXACTLY:**

1. **CONTEXT AWARENESS**: Always read and understand the ENTIRE conversation history before responding. Your response must make sense in the context of what we've been discussing.

2. **FOLLOW-UP COMMANDS**: When the user says:
   - "Simplify your response" → Make your IMMEDIATELY PREVIOUS response shorter and simpler
   - "Explain more" → Elaborate on your IMMEDIATELY PREVIOUS response  
   - "Give me one line answer" → Condense your PREVIOUS response to one sentence
   - "Tell me more about that" → Expand on the LAST topic you discussed

3. **MAINTAIN TOPIC FLOW**: If we're discussing menu items and user says "simplify," simplify the menu discussion - don't switch to general business advice.

4. **REFERENCE ACTUAL DATA**: Use the real customer review data above to answer questions about:
   - Best/worst comments
   - Common complaints
   - Customer praise
   - Areas for improvement

5. **BE CONVERSATIONAL**: Respond like a knowledgeable business partner who remembers everything we've discussed.

💡 **EXAMPLES OF CORRECT BEHAVIOR:**
User: "What trending items should I add?"
You: "Add nitro cold brew, matcha lattes, oat milk options..."
User: "Simplify your response"
You: "Add nitro cold brew, matcha lattes, and oat milk." ✅

WRONG BEHAVIOR:
User: "Simplify your response" 
You: "Here are 10 general business tips..." ❌

🎯 **YOUR EXPERTISE AREAS:**
- Review analysis using actual customer feedback above
- Menu suggestions and trending items
- Business operations and improvements
- Marketing and customer service advice
- Staff and inventory management

Remember: You're having a CONVERSATION with the cafe owner. Each response should connect to what we've been discussing. Always maintain context and topic continuity."""

        # Build messages array with FULL conversation history for context
        messages = [{"role": "system", "content": system_prompt}]
        
        # Include MORE chat history for better context understanding
        if request.chat_history:
            # Keep last 12 messages for better context (6 exchanges)
            recent_history = request.chat_history[-12:]  
            for msg in recent_history:
                messages.append({"role": msg.role, "content": msg.content})
        
        # Add current user question
        messages.append({"role": "user", "content": request.question})

        print(f"🚀 Calling Mistral 7B with {len(messages)} messages for context")

        # Use Mistral 7B Free - with better parameters for context understanding
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=messages,
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
            max_tokens=1500,  # Increased for better responses
            temperature=0.6,  # Lower temperature for more consistent context following
            timeout=30
        )
        
        answer = response["choices"][0]["message"]["content"]
        print(f"✅ Mistral 7B responded with context: {len(answer)} chars")
        
        return {"status": "success", "answer": answer}
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")
