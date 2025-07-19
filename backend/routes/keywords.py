# backend/routes/keywords.py
import httpx
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from collections import Counter, defaultdict
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer

router = APIRouter()

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    sia = SentimentIntensityAnalyzer()
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('vader_lexicon')
    from nltk.sentiment import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()

@router.get("/keyword-trends")
async def keyword_analysis():
    """
    Dynamic keyword analysis that adapts to actual review content
    """
    try:
        # Fetch reviews from existing endpoint
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("http://127.0.0.1:8000/get-reviews")
        
        if not resp.status_code == 200:
            raise Exception(f"Failed to fetch reviews: {resp.status_code}")
        
        data = resp.json()
        if data.get("status") != "success" or not isinstance(data.get("data"), list):
            raise Exception("Invalid reviews data")
        
        reviews = data["data"]
        
        if not reviews:
            return {
                "keywords": [],
                "total_keywords_analyzed": 0,
                "unique_keywords": 0,
                "total_reviews": 0
            }
        
        # Analyze each review dynamically
        sentiment_keywords = {"positive": [], "neutral": [], "negative": []}
        
        for review in reviews:
            text = review.get("review_text", "")
            rating = review.get("rating", 3)
            
            # Determine sentiment
            if rating >= 4:
                sentiment = "positive"
            elif rating >= 3:
                sentiment = "neutral"
            else:
                sentiment = "negative"
            
            # Extract meaningful keywords from actual text
            keywords = extract_dynamic_keywords(text)
            sentiment_keywords[sentiment].extend(keywords)
        
        # Get top keywords for each sentiment
        results = []
        
        # Get 3 positive keywords
        positive_counts = Counter(sentiment_keywords["positive"])
        top_positive = positive_counts.most_common(3)
        for keyword, count in top_positive:
            results.append({
                "keyword": keyword,
                "count": count,
                "sentiment_breakdown": {"positive": count, "neutral": 0, "negative": 0},
                "dominant_sentiment": "positive",
                "percentage": round((count / len(reviews)) * 100, 1)
            })
        
        # Get 3 neutral keywords
        neutral_counts = Counter(sentiment_keywords["neutral"])
        top_neutral = neutral_counts.most_common(3)
        for keyword, count in top_neutral:
            results.append({
                "keyword": keyword,
                "count": count,
                "sentiment_breakdown": {"positive": 0, "neutral": count, "negative": 0},
                "dominant_sentiment": "neutral",
                "percentage": round((count / len(reviews)) * 100, 1)
            })
        
        # Get 2 negative keywords
        negative_counts = Counter(sentiment_keywords["negative"])
        top_negative = negative_counts.most_common(2)
        for keyword, count in top_negative:
            results.append({
                "keyword": keyword,
                "count": count,
                "sentiment_breakdown": {"positive": 0, "neutral": 0, "negative": count},
                "dominant_sentiment": "negative",
                "percentage": round((count / len(reviews)) * 100, 1)
            })
        
        return {
            "keywords": results,
            "total_keywords_analyzed": sum(len(keywords) for keywords in sentiment_keywords.values()),
            "unique_keywords": len(set(sum(sentiment_keywords.values(), []))),
            "total_reviews": len(reviews)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_dynamic_keywords(text: str) -> List[str]:
    """
    Extract meaningful keywords from actual review text
    """
    if not text or len(text.strip()) < 3:
        return []
    
    text = text.lower()
    keywords = []
    
    # Enhanced stopwords for cafe context
    stop_words = set(stopwords.words('english'))
    cafe_stopwords = {
        'cafe', 'coffee', 'shop', 'place', 'time', 'get', 'go', 'came', 
        'went', 'really', 'also', 'would', 'could', 'should', 'one', 'two', 
        'three', 'got', 'said', 'say', 'come', 'back', 'like', 'much', 'well',
        'think', 'know', 'make', 'take', 'give', 'see', 'look', 'try', 'want',
        'need', 'lot', 'bit', 'little', 'big', 'small', 'right', 'wrong'
    }
    stop_words.update(cafe_stopwords)
    
    # Method 1: Extract meaningful adjectives and nouns
    tokens = word_tokenize(text)
    pos_tags = nltk.pos_tag(tokens)
    
    for word, pos in pos_tags:
        if (word.lower() not in stop_words and 
            len(word) > 2 and 
            word.isalpha() and
            pos in ['JJ', 'JJR', 'JJS', 'NN', 'NNS']):  # Adjectives and nouns
            keywords.append(word.lower())
    
    # Method 2: Extract specific cafe-related terms
    cafe_terms = {
        # Service terms
        'service': ['service', 'staff', 'waiter', 'waitress', 'barista', 'employee', 'worker'],
        'fast': ['fast', 'quick', 'speedy', 'rapid'],
        'slow': ['slow', 'sluggish', 'waited', 'waiting'],
        'friendly': ['friendly', 'nice', 'kind', 'polite', 'helpful'],
        'rude': ['rude', 'unfriendly', 'impolite', 'mean'],
        
        # Quality terms
        'delicious': ['delicious', 'tasty', 'yummy', 'amazing', 'excellent'],
        'bad': ['bad', 'terrible', 'awful', 'horrible', 'disgusting'],
        'fresh': ['fresh', 'hot', 'warm'],
        'cold': ['cold', 'lukewarm', 'stale'],
        
        # Price terms
        'expensive': ['expensive', 'pricey', 'costly', 'overpriced'],
        'cheap': ['cheap', 'affordable', 'reasonable'],
        'value': ['value', 'worth'],
        
        # Atmosphere terms
        'cozy': ['cozy', 'comfortable', 'relaxing', 'peaceful'],
        'noisy': ['noisy', 'loud', 'chaotic'],
        'clean': ['clean', 'tidy', 'spotless'],
        'dirty': ['dirty', 'messy', 'unclean'],
        
        # General experience
        'love': ['love', 'loved', 'amazing', 'perfect'],
        'hate': ['hate', 'hated', 'dislike', 'disappointed']
    }
    
    # Find cafe-specific terms in the text
    for main_term, variations in cafe_terms.items():
        for variation in variations:
            if variation in text:
                keywords.append(main_term)
                break
    
    # Method 3: Extract common phrases
    phrases = [
        'customer service', 'great coffee', 'long wait', 'wait time',
        'good value', 'too expensive', 'highly recommend', 'come back',
        'friendly staff', 'rude staff', 'clean place', 'dirty place'
    ]
    
    for phrase in phrases:
        if phrase in text:
            keywords.append(phrase.replace(' ', '_'))  # Replace spaces for consistency
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen and len(keyword) > 2:
            seen.add(keyword)
            unique_keywords.append(keyword)
    
    return unique_keywords
