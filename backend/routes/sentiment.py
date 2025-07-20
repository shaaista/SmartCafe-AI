from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from nltk.sentiment import SentimentIntensityAnalyzer
from supabase_client import supabase
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize sentiment analyzer
try:
    sia = SentimentIntensityAnalyzer()
except:
    import nltk
    nltk.download('vader_lexicon')
    from nltk.sentiment import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()

@router.get("/sentiment")
async def sentiment_analysis():
    """Returns sentiment analysis on all reviews"""
    try:
        logger.info("Fetching reviews for sentiment analysis...")
        
        # Use 'timestamp' column as shown in your table
        response = supabase.table("reviews").select("*").order("timestamp", desc=True).execute()
        
        if not response.data:
            logger.info("No reviews found for sentiment analysis")
            return {
                "counts": {"positive": 0, "neutral": 0, "negative": 0},
                "labels": [],
                "total": 0
            }
        
        reviews = response.data
        logger.info(f"Analyzing sentiment for {len(reviews)} reviews")

        # Sentiment calculation
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        sentiment_labels = []
        
        for review in reviews:
            text = review.get("review_text", "")
            rating = review.get("rating", 3)
            
            # Use both VADER sentiment and rating for more accurate classification
            scores = sia.polarity_scores(text)
            compound = scores['compound']
            
            # Combine VADER score with rating for better accuracy
            if compound >= 0.05 and rating >= 4:
                label = "positive"
            elif compound <= -0.05 or rating <= 2:
                label = "negative"
            else:
                label = "neutral"
            
            sentiment_counts[label] += 1
            sentiment_labels.append({
                "id": review.get("id"),
                "review_text": text,
                "sentiment": label,
                "compound": compound,
                "timestamp": review.get("timestamp"),
                "rating": rating,
            })

        result = {
            "counts": sentiment_counts,
            "labels": sentiment_labels,
            "total": len(reviews)
        }
        
        logger.info(f"Sentiment analysis complete: {sentiment_counts}")
        return result

    except Exception as e:
        logger.error(f"Sentiment analysis error: {str(e)}")
        return {
            "counts": {"positive": 0, "neutral": 0, "negative": 0},
            "labels": [],
            "total": 0
        }
