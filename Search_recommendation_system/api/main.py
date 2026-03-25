from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.session import init_db
from api.routes import router

app = FastAPI(
    title="Search Recommendation System",
    description=(
        "Reranks search results using TF-IDF similarity + "
        "position-bias-corrected CTR + recency signals from user click data."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "Search Recommendation API",
        "docs": "/docs",
        "endpoints": {
            "search (unranked)": "/api/v1/search?q=<query>",
            "recommend (reranked)": "/api/v1/recommend?q=<query>",
            "log click": "POST /api/v1/click",
            "log impression": "POST /api/v1/impression",
            "stats": "/api/v1/stats",
        },
    }