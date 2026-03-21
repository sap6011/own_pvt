from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ---- Request bodies ---- #

class ClickRequest(BaseModel):
    query: str
    result_id: int
    position: int
    session_id: str


class ImpressionRequest(BaseModel):
    query: str
    result_id: int
    position: int
    session_id: str


# ---- Response models ---- #

class SearchResultOut(BaseModel):
    id: int
    title: str
    content: str
    url: str

    class Config:
        from_attributes = True


class RankedResultOut(BaseModel):
    id: int
    title: str
    content: str
    url: str
    score: float
    tfidf_sim: float
    corrected_ctr: float
    recency_score: float
    impressions: int


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultOut]


class RecommendResponse(BaseModel):
    query: str
    alpha: float
    beta: float
    gamma: float
    results: list[RankedResultOut]


class ClickResponse(BaseModel):
    status: str
    message: str


class StatsResponse(BaseModel):
    total_results: int
    total_impressions: int
    total_clicks: int
    unique_queries: int
