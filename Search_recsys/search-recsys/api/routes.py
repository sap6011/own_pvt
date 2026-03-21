"""
routes.py
---------
All API endpoints.

GET  /search      — returns raw (unranked) candidate results
GET  /recommend   — returns TF-IDF + CTR reranked results  ← the main endpoint
POST /click       — log a click event
POST /impression  — log an impression event
GET  /stats       — system stats (good for demos)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.session import get_db
from db.models import SearchResult, ClickEvent, Impression
from model.scorer import rerank
from api.schemas import (
    ClickRequest, ImpressionRequest,
    SearchResponse, RecommendResponse,
    ClickResponse, StatsResponse,
    SearchResultOut, RankedResultOut,
)

router = APIRouter()


# --------------------------------------------------------------------------- #
# /search  — naive keyword search, no reranking                               #
# --------------------------------------------------------------------------- #
@router.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Returns up to `limit` results matching the query (simple LIKE search).
    No personalisation — use /recommend for reranked results.
    """
    results = (
        db.query(SearchResult)
        .filter(
            SearchResult.title.ilike(f"%{q}%")
            | SearchResult.content.ilike(f"%{q}%")
        )
        .limit(limit)
        .all()
    )

    # If nothing matches, fall back to returning all docs (demo friendliness)
    if not results:
        results = db.query(SearchResult).limit(limit).all()

    return SearchResponse(query=q, results=[SearchResultOut.from_orm(r) for r in results])


# --------------------------------------------------------------------------- #
# /recommend  — reranked results using TF-IDF + CTR                           #
# --------------------------------------------------------------------------- #
@router.get("/recommend", response_model=RecommendResponse)
def recommend(
    q: str   = Query(..., description="Search query"),
    limit: int   = Query(10, ge=1, le=50),
    alpha: float = Query(0.4, ge=0.0, le=1.0, description="TF-IDF weight"),
    beta:  float = Query(0.4, ge=0.0, le=1.0, description="CTR weight"),
    gamma: float = Query(0.2, ge=0.0, le=1.0, description="Recency weight"),
    db: Session  = Depends(get_db),
):
    """
    Reranks search results using a blend of:
    - **alpha** × TF-IDF text similarity
    - **beta**  × position-bias-corrected click-through rate
    - **gamma** × recency-weighted click score
    """
    candidates = db.query(SearchResult).all()
    ranked = rerank(query=q, results=candidates, db=db, alpha=alpha, beta=beta, gamma=gamma)
    top = ranked[:limit]

    return RecommendResponse(
        query=q,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
        results=[RankedResultOut(**r) for r in top],
    )


# --------------------------------------------------------------------------- #
# /click  — log a user click                                                  #
# --------------------------------------------------------------------------- #
@router.post("/click", response_model=ClickResponse)
def log_click(body: ClickRequest, db: Session = Depends(get_db)):
    """Records that a user clicked result `result_id` at position `position`."""
    event = ClickEvent(
        query=body.query,
        result_id=body.result_id,
        position=body.position,
        session_id=body.session_id,
    )
    db.add(event)
    db.commit()
    return ClickResponse(status="ok", message="Click recorded.")


# --------------------------------------------------------------------------- #
# /impression  — log what was shown to the user                               #
# --------------------------------------------------------------------------- #
@router.post("/impression", response_model=ClickResponse)
def log_impression(body: ImpressionRequest, db: Session = Depends(get_db)):
    """Records that result `result_id` was shown at position `position`."""
    imp = Impression(
        query=body.query,
        result_id=body.result_id,
        position=body.position,
        session_id=body.session_id,
    )
    db.add(imp)
    db.commit()
    return ClickResponse(status="ok", message="Impression recorded.")


# --------------------------------------------------------------------------- #
# /stats  — quick system overview                                              #
# --------------------------------------------------------------------------- #
@router.get("/stats", response_model=StatsResponse)
def stats(db: Session = Depends(get_db)):
    return StatsResponse(
        total_results=db.query(SearchResult).count(),
        total_impressions=db.query(Impression).count(),
        total_clicks=db.query(ClickEvent).count(),
        unique_queries=db.query(func.count(func.distinct(ClickEvent.query))).scalar(),
    )
