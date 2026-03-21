"""
features.py
-----------
Computes per-(query, result) features from raw click logs stored in the DB.

Features
--------
ctr             : clicks / impressions  (position-bias-corrected)
recency_score   : exponentially decaying weight of recent clicks
impression_count: raw number of times shown for this (query, result) pair
"""

from datetime import datetime, timedelta
import math
from sqlalchemy.orm import Session
from db.models import ClickEvent, Impression


def position_bias_correction(position: int) -> float:
    """
    Inverse of the click probability boost from position.
    We use this to debias CTR: true_ctr ≈ raw_ctr / bias(pos).
    """
    return 1.0 / (1 + 0.5 * (position - 1))


def compute_ctr_features(query: str, result_id: int, db: Session) -> dict:
    """
    Returns position-bias-corrected CTR and impression count
    for a given (query, result_id) pair.
    """
    impressions = (
        db.query(Impression)
        .filter(Impression.query == query, Impression.result_id == result_id)
        .all()
    )
    clicks = (
        db.query(ClickEvent)
        .filter(ClickEvent.query == query, ClickEvent.result_id == result_id)
        .all()
    )

    impression_count = len(impressions)
    if impression_count == 0:
        return {"ctr": 0.0, "corrected_ctr": 0.0, "impression_count": 0}

    # Raw CTR
    raw_ctr = len(clicks) / impression_count

    # Position-bias-corrected CTR:
    # weight each impression by 1/bias(pos) so lower-position impressions
    # don't inflate the denominator unfairly.
    weighted_impressions = sum(
        1 / position_bias_correction(imp.position) for imp in impressions
    )
    weighted_clicks = sum(
        1 / position_bias_correction(c.position) for c in clicks
    )
    corrected_ctr = weighted_clicks / weighted_impressions if weighted_impressions > 0 else 0.0

    return {
        "ctr": raw_ctr,
        "corrected_ctr": corrected_ctr,
        "impression_count": impression_count,
    }


def compute_recency_score(query: str, result_id: int, db: Session,
                           half_life_hours: float = 72.0) -> float:
    """
    Exponentially decaying sum of clicks — recent clicks matter more.
    score = Σ  exp(-λ * age_in_hours)   for each click event
    where λ = ln(2) / half_life_hours
    """
    clicks = (
        db.query(ClickEvent)
        .filter(ClickEvent.query == query, ClickEvent.result_id == result_id)
        .all()
    )
    if not clicks:
        return 0.0

    lam = math.log(2) / half_life_hours
    now = datetime.utcnow()
    score = sum(
        math.exp(-lam * max((now - c.timestamp).total_seconds() / 3600, 0))
        for c in clicks
    )
    return score


def get_all_features(query: str, result_id: int, db: Session) -> dict:
    """Returns the full feature dict for one (query, result) pair."""
    ctr_features = compute_ctr_features(query, result_id, db)
    recency = compute_recency_score(query, result_id, db)
    return {**ctr_features, "recency_score": recency}
