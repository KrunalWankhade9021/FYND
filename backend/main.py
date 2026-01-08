from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from pydantic import BaseModel
from typing import List
from datetime import datetime
import os
import tempfile
import llm_service

# ==========================
# 1. DATABASE CONFIGURATION
# ==========================
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Render provides 'postgres://' but SQLAlchemy needs 'postgresql://'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    SQL_ALCHEMY_DATABASE_URL = DATABASE_URL
    connect_args = {} # No special args for Postgres
    print("Using Production Database (PostgreSQL)")
else:
    # Use a temp directory for the DB to avoid triggering "Live Server" reloads
    temp_dir = tempfile.gettempdir()
    db_path = os.path.join(temp_dir, "feedback.db")
    SQL_ALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
    connect_args = {"check_same_thread": False}
    print(f"Using Local Database: {db_path}")

engine = create_engine(
    SQL_ALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================
# 2. MODELS (DB Tables)
# ==========================
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer)
    review = Column(String)
    # AI Generated Fields
    ai_response = Column(String, default="")
    summary = Column(String, default="")
    recommended_action = Column(String, default="")
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables immediately
Base.metadata.create_all(bind=engine)

# ==========================
# 3. SCHEMAS (Pydantic)
# ==========================
class ReviewBase(BaseModel):
    rating: int
    review: str

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(BaseModel):
    success: bool
    ai_response: str

class AdminReview(ReviewBase):
    id: int
    ai_response: str
    summary: str
    recommended_action: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class AdminReviewList(BaseModel):
    count: int
    data: List[AdminReview]

# ==========================
# 4. FASTAPI APP
# ==========================
app = FastAPI(title="Feedback AI System", version="1.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/reviews", response_model=ReviewResponse)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """Endpoint for user review submission (User Dashboard)."""
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # AI Processing
    ai_response = llm_service.generate_response(review.rating, review.review)
    summary, action = llm_service.generate_admin_insights(review.rating, review.review)
    
    # DB Storage
    db_review = Review(
        rating=review.rating,
        review=review.review,
        ai_response=ai_response,
        summary=summary,
        recommended_action=action
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    return {"success": True, "ai_response": ai_response}

@app.get("/admin/reviews", response_model=AdminReviewList)
def get_reviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Endpoint for fetching all reviews (Admin Dashboard)."""
    reviews = db.query(Review).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
    count = db.query(Review).count()
    return {"count": count, "data": reviews}
