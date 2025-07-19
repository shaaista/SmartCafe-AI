# backend/routes/sentiment.py
from fastapi import APIRouter, HTTPException
import httpx
from typing import List, Dict, Any
from nltk.sentiment import SentimentIntensityAnalyzer

router = APIRouter()

# Make sure nltk vader_lexicon is downloaded, or handle error gracefully.
try:
    sia = SentimentIntensityAnalyzer()
except:
    import nltk
    nltk.download('vader_lexicon')
    from nltk.sentiment import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()

@router.get("/sentiment")
async def sentiment_analysis():
    """
    Returns sentiment analysis on all reviews.
    Labels: positive, negative, neutral.
    Output: count per label, plus each review's sentiment.
    """
    try:
        # The reviews endpoint must return JSON:
        # {"status":"success", "data": [ {review_text, rating, timestamp, ...}, ... ]}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("http://127.0.0.1:8000/get-reviews")
        if not resp.status_code == 200:
            raise Exception(f"Failed to fetch reviews: {resp.status_code}")
        data = resp.json()
        if data.get("status") != "success" or not isinstance(data.get("data"), list):
            raise Exception("Invalid reviews data")
        reviews = data["data"]

        # Sentiment calculation
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        sentiment_labels = []
        for review in reviews:
            text = review.get("review_text", "")
            scores = sia.polarity_scores(text)
            compound = scores['compound']
            if compound >= 0.05:
                label = "positive"
            elif compound <= -0.05:
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
                "rating": review.get("rating"),
            })

        result = {
            "counts": sentiment_counts,            # for charting
            "labels": sentiment_labels,            # for detailed UI if needed
            "total": len(reviews)
        }
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
