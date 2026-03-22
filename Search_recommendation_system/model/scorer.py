from typing import List
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from db.models import SearchResult
from pipeline.features import get_all_features

DEFAULT_ALPHA = 0.4
DEFAULT_BETA  = 0.4
DEFAULT_GAMMA = 0.2

def _normalize(values: List[float]) -> List[float]:
    arr = np.array(values, dtype=float)
    mn, mx = arr.min(), arr.max()
    if mx == mn:
        return [0.0] * len(values)
    return ((arr - mn) / (mx - mn)).tolist()

def tfidf_similarity(query: str, documents: List[SearchResult], db: Session) -> List[float]:
    #  TF-IDF similarity calculation
    if not documents:
        return []
    corpus = [query] + documents
    vetorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vetorizer.fit_transform(corpus)
    sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten() # type: ignore
    return sims.tolist()

def rereank(query: str, results: List[SearchResult], db: Session, alpha: float = DEFAULT_ALPHA, beta: float = DEFAULT_BETA, gamma: float = DEFAULT_GAMMA) -> List[SearchResult]:
    if not results:
        return []
    
    doc_texts = [f"{r.title} {r.content}" for r in results]
    tfidf_sims = tfidf_similarity(query, doc_texts)   # type: ignore
    features = [get_all_features(query, r.id, db) for r in results] # type: ignore
    ctrs = [f["ctr"] for f in features]
    recencies = [f["recency_score"] for f in features]
    tfidf_norm = _normalize(tfidf_sims)
    ctr_norm = _normalize(ctrs)
    recency_norm = _normalize(recencies)
    scored = []
    
    for i, result in enumerate(results):
        final_score = alpha * tfidf_norm[i] + beta * ctr_norm[i] + gamma * recency_norm[i]

        scored.append(
            {
                "id": result.id,
                "title": result.title,
                "content": result.content,
                "url": result.url,
                "score":round(final_score, 4),
                "tfidf_sim": round(tfidf_sims[i], 4),
                "corrected_ctr": round(ctrs[i], 4),
                "recency_score": round(recencies[i], 4),
                "impressions": features[i]["impression_count"]
            }
        )
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored
