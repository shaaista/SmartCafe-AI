from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from collections import Counter, defaultdict
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from supabase_client import supabase
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

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
    """Smart keyword analysis focused on cafe-specific meaningful terms"""
    try:
        logger.info("Starting intelligent keyword analysis...")
        
        # Fetch reviews directly from Supabase
        response = supabase.table("reviews").select("*").execute()
        
        if not response.data:
            return {
                "keywords": [],
                "total_keywords_analyzed": 0,
                "unique_keywords": 0,
                "total_reviews": 0
            }
        
        reviews = response.data
        logger.info(f"Analyzing {len(reviews)} reviews for meaningful keywords")
        
        # Extract smart keywords from all reviews
        all_keywords = []
        for review in reviews:
            text = review.get("review_text", "")
            rating = review.get("rating", 3)
            
            # Get cafe-specific keywords
            keywords = extract_smart_cafe_keywords(text, rating)
            all_keywords.extend(keywords)
        
        # Count keyword frequencies
        keyword_counts = Counter(all_keywords)
        
        # Get top 8 most relevant keywords
        top_keywords = keyword_counts.most_common(8)
        
        # Format results with additional context
        results = []
        total_reviews = len(reviews)
        
        for keyword, count in top_keywords:
            percentage = round((count / total_reviews) * 100, 1)
            results.append({
                "keyword": keyword.title(),  # Capitalize for better presentation
                "count": count,
                "percentage": percentage,
                "relevance_score": calculate_relevance_score(keyword, count, total_reviews)
            })
        
        logger.info(f"Generated {len(results)} relevant keywords")
        return {
            "keywords": results,
            "total_keywords_analyzed": len(all_keywords),
            "unique_keywords": len(set(all_keywords)),
            "total_reviews": total_reviews
        }
        
    except Exception as e:
        logger.error(f"Keywords analysis error: {str(e)}")
        return {
            "keywords": [],
            "total_keywords_analyzed": 0,
            "unique_keywords": 0,
            "total_reviews": 0
        }

def extract_smart_cafe_keywords(text: str, rating: int) -> List[str]:
    """Extract only meaningful, cafe-relevant keywords from review text"""
    if not text or len(text.strip()) < 3:
        return []
    
    text = text.lower().strip()
    keywords = []
    
    # Cafe-specific keyword categories with variations
    cafe_keyword_map = {
        # Service Quality
        "excellent_service": ["excellent service", "great service", "amazing service", "outstanding service", "exceptional service"],
        "poor_service": ["poor service", "bad service", "terrible service", "awful service", "horrible service"],
        "fast_service": ["quick service", "fast service", "speedy service", "prompt service"],
        "slow_service": ["slow service", "sluggish service", "delayed service"],
        "friendly_staff": ["friendly staff", "nice staff", "kind staff", "helpful staff", "polite staff", "courteous staff"],
        "rude_staff": ["rude staff", "unfriendly staff", "impolite staff", "mean staff"],
        
        # Food & Beverage Quality
        "great_coffee": ["amazing coffee", "excellent coffee", "great coffee", "perfect coffee", "delicious coffee", "fantastic coffee"],
        "bad_coffee": ["terrible coffee", "awful coffee", "bad coffee", "horrible coffee", "disgusting coffee"],
        "strong_coffee": ["strong coffee", "bold coffee", "rich coffee"],
        "weak_coffee": ["weak coffee", "watery coffee", "bland coffee"],
        "fresh_food": ["fresh food", "fresh pastries", "fresh sandwiches"],
        "stale_food": ["stale food", "old food", "stale pastries"],
        
        # Pricing
        "expensive": ["expensive", "overpriced", "too pricey", "costly", "high prices"],
        "affordable": ["affordable", "reasonable prices", "good value", "cheap", "inexpensive"],
        "great_value": ["great value", "good value", "worth it", "value for money"],
        
        # Atmosphere & Environment
        "cozy_atmosphere": ["cozy", "comfortable", "relaxing", "peaceful", "warm atmosphere", "inviting"],
        "noisy": ["noisy", "loud", "chaotic", "too loud"],
        "clean": ["clean", "spotless", "tidy", "well-maintained", "hygienic"],
        "dirty": ["dirty", "messy", "unclean", "filthy", "unsanitary"],
        "nice_decor": ["beautiful decor", "nice decor", "lovely interior", "great ambiance", "cute place"],
        
        # Wait Time
        "long_wait": ["long wait", "slow service", "waited forever", "took too long"],
        "quick_service": ["quick", "fast", "no wait", "immediate service"],
        
        # Overall Experience
        "highly_recommend": ["highly recommend", "definitely recommend", "must visit", "come back"],
        "disappointed": ["disappointed", "let down", "not impressed", "underwhelmed"],
        "love_this_place": ["love this place", "favorite cafe", "best cafe", "amazing place"],
        
        # Specific Items
        "great_pastries": ["delicious pastries", "amazing pastries", "fresh pastries", "great bakery items"],
        "good_wifi": ["good wifi", "fast internet", "reliable wifi"],
        "limited_seating": ["crowded", "no seats", "packed", "busy"],
        
        # Special Features (based on your reviews mentioning a cat)
        "cafe_cat": ["cat", "kitty", "cute cat", "friendly cat"],
    }
    
    # Extract keywords based on exact phrase matches
    for main_keyword, variations in cafe_keyword_map.items():
        for variation in variations:
            if variation in text:
                keywords.append(main_keyword.replace('_', ' '))
                break  # Only add once per main category
    
    # Extract single meaningful adjectives (quality-focused)
    quality_adjectives = {
        'delicious', 'tasty', 'amazing', 'excellent', 'outstanding', 'perfect', 'wonderful',
        'terrible', 'awful', 'horrible', 'disgusting', 'bland', 'bitter',
        'friendly', 'helpful', 'rude', 'unprofessional',
        'clean', 'dirty', 'fresh', 'stale',
        'expensive', 'cheap', 'overpriced', 'affordable',
        'cozy', 'comfortable', 'noisy', 'crowded', 'spacious',
        'fast', 'slow', 'quick', 'prompt'
    }
    
    # Tokenize and check for quality adjectives
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    for word in words:
        if word.lower() in quality_adjectives and len(word) > 3:
            keywords.append(word.lower())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen and len(keyword) > 2:
            seen.add(keyword)
            unique_keywords.append(keyword)
    
    return unique_keywords[:5]  # Limit to 5 keywords per review

def calculate_relevance_score(keyword: str, count: int, total_reviews: int) -> float:
    """Calculate relevance score for keyword ranking"""
    frequency_score = count / total_reviews
    
    # Boost score for highly relevant cafe terms
    relevance_multipliers = {
        'service': 1.5,
        'coffee': 1.5,
        'staff': 1.4,
        'food': 1.3,
        'atmosphere': 1.3,
        'clean': 1.2,
        'friendly': 1.2,
        'delicious': 1.2,
        'expensive': 1.1,
        'cozy': 1.1
    }
    
    multiplier = 1.0
    for term, mult in relevance_multipliers.items():
        if term in keyword.lower():
            multiplier = mult
            break
    
    return round(frequency_score * multiplier * 100, 2)
