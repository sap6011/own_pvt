from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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

class SearchResultOut(BaseModel):
    id: int
    title: str
    content: str
    url: str
    
    class Config:
        from_attributes = True

class RerankedResultOut(BaseModel):
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

class RecommendationResponse(BaseModel):
    query: str
    alpha: float
    beta: float 
    gamma: float
    results: list[RerankedResultOut]

class ClickResponse(BaseModel):
    status: str
    message: str
class StatsResponse(BaseModel):
    unique_queries: int
    total_impressions: int
    total_clicks: int   
    total_results: int




    