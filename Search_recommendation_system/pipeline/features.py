import math
from datetime import datetime
from sqlalchemy.orm import Session
from db.models import Impression, ClickEvent

def position_bias_correction(position: int) -> float:
    """
    Calculate position bias correction factor.
    We define it here again because this is where it's actually used for real correction — 
    in the simulator it was just for generating fake data, here it's for debiasing real click data.
    """
    return 1.0 / (1 + 0.5 * (position - 1)) 

def compute_ctr_features(query: str, result_id: int, db: Session) -> dict:
    impressions = (
        db.query(Impression).filter(Impression.query == query, Impression.result_id == result_id).all()
    )

    clicks = (
        db.query(ClickEvent).filter(ClickEvent.query == query, ClickEvent.result_id == result_id).all()
    )

    impression_count = len(impressions)
    if impression_count == 0:
        return {
            "ctr": 0.0,
            "corrected_ctr": 0.0,
            "impression_count": 0

        }
    raw_ctr = len(clicks) / impression_count

    weighted_impressions = sum(
        1 / position_bias_correction(imp.position) for imp in impressions # type: ignore
    )
    weighted_clicks = sum(
        1 / position_bias_correction(c.position) for c in clicks # type: ignore
    )
    corrected_ctr = weighted_clicks / weighted_impressions if weighted_impressions > 0 else 0.0

    return {
        "ctr": raw_ctr,
        "corrected_ctr": corrected_ctr,
        "impression_count": impression_count,
    }

def compute_recency_Score(query: str, result_id: int, db: Session, half_life_hours: float = 72.0) -> float:
    
    clicks = (
        db.query(ClickEvent).filter(ClickEvent.query == query, ClickEvent.result_id == result_id).all()
    )
    if not clicks:
        return 0.0
    
    lam = math.log(2) / half_life_hours
    now = datetime.utcnow()
    score = sum(math.exp(-lam * (now - c.timestamp).total_seconds() / 3600, 0) for c in clicks) # type: ignore
    return score

def get_all_features(query: str, result_id: int, db: Session) -> dict:
    ctr_features = compute_ctr_features(query, result_id, db)
    recency_score = compute_recency_Score(query, result_id, db)
    return {
        **ctr_features,
        "recency_score": recency_score
    }
 