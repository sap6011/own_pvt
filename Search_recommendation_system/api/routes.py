from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

# from Search_recommendation_system import db
from db.session import get_db
from db.models import SearchResult, ClickEvent, Impression

from model.scorer import rerank
from api.schemas import (
    ClickRequest, ImpressionRequest,
    SearchResponse, RecommendationResponse,
    ClickResponse, StatsResponse,
    SearchResultOut, RerankedResultOut,
)
router = APIRouter()

@router.get("/search", response_model=SearchResponse)
def Search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50), 
    db: Session = Depends(get_db)
    ):
    results = (
        db.query(SearchResult).filter(
            SearchResult.title.ilike(f"%{q}%") | SearchResult.content.ilike(f"%{q}%")
        ).limit(limit).all()
    )
    if not results:
        results = db.query(SearchResult).limit(limit).all()
    return SearchResponse(
        query=q,
        results=[SearchResultOut.from_orm(r) for r in results]
    )

@router.get("/recommend", response_model=RecommendationResponse)
def Recommend(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    alpha: float = Query(0.4, ge=0.0, le=1.0, description="Weight for TF-IDF similarity"),
    beta: float = Query(0.4, ge=0.0, le=1.0, description="Weight for CTR"),
    gamma: float = Query(0.2, ge=0.0, le=1.0, description="Weight for recency score"),
    db: Session  = Depends(get_db)
):
    candidates = db.query(SearchResult).all()
    ranked = rerank(query = q, results=candidates, db=db, alpha=alpha, beta=beta, gamma=gamma)
    top = ranked[:limit]
    return RecommendationResponse(
        query=q,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
        results=[RerankedResultOut(**r) for r in top]
    )

@router.post("/click", response_model=ClickResponse)
def log_click(body: ClickRequest, db: Session = Depends(get_db)):
    event = ClickEvent(
        query=body.query,
        result_id=body.result_id,
        position=body.position,
        session_id=body.session_id,
    )
    db.add(event)
    db.commit()
    return ClickResponse(status="ok", message="Click recorded.")

@router.post("/impression", response_model=ClickResponse)
def log_impression(body: ImpressionRequest, db: Session = Depends(get_db)):
    imp = Impression(
        query=body.query,
        result_id=body.result_id,
        position=body.position,
        session_id=body.session_id,
    )
    db.add(imp)
    db.commit()
    return ClickResponse(status="ok", message="Impression recorded.")

@router.get("/stats", response_model=StatsResponse)
def stats(db: Session = Depends(get_db)):
    return StatsResponse(
        total_results=db.query(SearchResult).count(),
        total_impressions=db.query(Impression).count(),
        total_clicks=db.query(ClickEvent).count(),
        unique_queries=db.query(func.count(func.distinct(ClickEvent.query))).scalar(),
    )


