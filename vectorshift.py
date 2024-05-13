from fastapi import FastAPI, Depends
from datetime import datetime
from typing import List, Optional
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uvicorn

# Define database model
Base = declarative_base()
engine = create_engine('sqlite:///sentiment.db')  # Change path if needed
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class SentimentData(Base):
    __tablename__ = 'sentiment_data'

    id = Column(Integer, primary_key=True)
    text = Column(String)
    sentiment_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

def analyze_sentiment(text: str, split_size: int = 100) -> List[dict]:
    """
    Analyzes the sentiment of a given text by splitting it into chunks of a specified size and calculating the sentiment score for each chunk.

    Args:
        text (str): The text to analyze.
        split_size (int, optional): The size of each chunk to split the text into. Defaults to 100.

    Returns:
        List[dict]: A list of dictionaries containing the chunk of text and its corresponding sentiment score.

    """
    analyzer = SentimentIntensityAnalyzer()
    start_time = time.time()
    results = []
    words = text.split()

    for i in range(0, len(words), split_size):
        chunk = ' '.join(words[i:i + split_size])
        print(chunk)
        score = analyzer.polarity_scores(chunk)
        results.append({"text": chunk, "sentiment_score": score["compound"]})

    total_time = time.time() - start_time
    print(f"Sentiment Analysis Time: {total_time:.2f} seconds")
    return results

def save_data(data: List[dict], db):
    start_time = time.time()
    for item in data:
        db.add(SentimentData(text=item["text"], sentiment_score=item["sentiment_score"]))
    db.commit()
    total_time = time.time() - start_time
    print(f"Data Saving Time: {total_time:.2f} seconds")



@app.post("/analyze")
def analyze(text: str, split_size: Optional[int] = 100, db = Depends(get_db)):
    data = analyze_sentiment(text, split_size)
    save_data(data, db)
    return {"message": "Data analyzed and saved successfully"}

@app.get("/ping")
def ping():
    return {"message": "Pong!"}


if __name__ == "__main__":
    uvicorn.run("__main__:app", host="0.0.0.0", port=80, reload=True)
