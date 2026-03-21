"""
scorer.py
---------
Combines TF-IDF text similarity with click-based signals to rerank results.

Final score
-----------
score = α * tfidf_sim  +  β * corrected_ctr  +  γ * recency_score_norm

All three components are normalised to [0, 1] before combining so the
weights α, β, γ are directly interpretable as "how much do I trust each signal".
"""

from typing import List
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from db.models import SearchResult
from pipeline.features import get_all_features


# Default blending weights (must sum to 1 for interpretability, but not required)
DEFAULT_ALPHA = 0.4   # text similarity weight
DEFAULT_BETA  = 0.4   # CTR weight
DEFAULT_GAMMA = 0.2   # recency weight


def _normalize(values: List[float]) -> List[float]:
    """Min-max normalise a list to [0, 1]. Returns zeros if all equal."""
    arr = np.array(values, dtype=float)
    mn, mx = arr.min(), arr.max()
    if mx == mn:
        return [0.0] * len(values)
    return ((arr - mn) / (mx - mn)).tolist()


def tfidf_similarity(query: str, documents: List[str]) -> List[float]:
    """
    Compute cosine similarity between the query and each document
    using TF-IDF vectors.
    """
    if not documents:
        return []
    corpus = [query] + documents
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)
    # query is the first row; compute similarity against all docs
    sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    return sims.tolist()


def rerank(
    query: str,
    results: List[SearchResult],
    db: Session,
    alpha: float = DEFAULT_ALPHA,
    beta: float  = DEFAULT_BETA,
    gamma: float = DEFAULT_GAMMA,
) -> List[dict]:
    """
    Given a list of candidate SearchResult ORM objects, return them reranked
    as a list of dicts (result + score breakdown), best first.

    Parameters
    ----------
    query   : the user's search query string
    results : candidate results fetched from DB
    db      : active SQLAlchemy session
    alpha   : weight for TF-IDF text similarity
    beta    : weight for position-bias-corrected CTR
    gamma   : weight for recency score
    """
    if not results:
        return []

    # ---- 1. TF-IDF similarity ---- #
    doc_texts = [f"{r.title} {r.content}" for r in results]
    tfidf_sims = tfidf_similarity(query, doc_texts)

    # ---- 2. Click features per result ---- #
    features = [get_all_features(query, r.id, db) for r in results]
    ctrs      = [f["corrected_ctr"]  for f in features]
    recencies = [f["recency_score"]  for f in features]

    # ---- 3. Normalise each signal ---- #
    tfidf_norm   = _normalize(tfidf_sims)
    ctr_norm     = _normalize(ctrs)
    recency_norm = _normalize(recencies)

    # ---- 4. Blend ---- #
    scored = []
    for i, result in enumerate(results):
        final_score = (
            alpha * tfidf_norm[i]
            + beta  * ctr_norm[i]
            + gamma * recency_norm[i]
        )
        scored.append({
            "id":            result.id,
            "title":         result.title,
            "content":       result.content,
            "url":           result.url,
            "score":         round(final_score, 4),
            "tfidf_sim":     round(tfidf_sims[i], 4),
            "corrected_ctr": round(ctrs[i], 4),
            "recency_score": round(recencies[i], 4),
            "impressions":   features[i]["impression_count"],
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored
