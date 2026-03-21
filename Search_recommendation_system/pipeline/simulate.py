import random
import uuid
from datetime import datetime, timedelta

from db.session import SessionLocal, init_db
from db.models import SearchResult, Impression, ClickEvent


DOCUMENTS = [
    ("Python Tutorial for Beginners",
     "Learn Python programming from scratch. Covers variables, loops, functions, and OOP.",
     "https://example.com/python-tutorial"),
    ("Advanced Python: Decorators and Metaclasses",
     "Deep dive into Python decorators, context managers, and metaclass programming.",
     "https://example.com/advanced-python"),
    ("FastAPI Documentation",
     "FastAPI is a modern, fast web framework for building APIs with Python and type hints.",
     "https://example.com/fastapi-docs"),
    ("Flask vs FastAPI: Which Should You Use?",
     "A detailed comparison of Flask and FastAPI for building REST APIs in Python.",
     "https://example.com/flask-vs-fastapi"),
    ("SQLAlchemy ORM Tutorial",
     "Learn how to use SQLAlchemy to interact with SQL databases using Python objects.",
     "https://example.com/sqlalchemy-orm"),
    ("Introduction to Machine Learning",
     "A beginner-friendly overview of supervised, unsupervised, and reinforcement learning.",
     "https://example.com/intro-ml"),
    ("Building Recommendation Systems",
     "Explains collaborative filtering, content-based filtering, and hybrid recommendation approaches.",
     "https://example.com/recsys"),
    ("TF-IDF Explained Simply",
     "How TF-IDF works for text similarity and information retrieval with Python examples.",
     "https://example.com/tfidf"),
    ("Understanding REST APIs",
     "What are REST APIs? Learn about endpoints, HTTP verbs, status codes, and JSON.",
     "https://example.com/rest-apis"),
    ("Docker for Python Developers",
     "Containerise your Python FastAPI application with Docker and docker-compose.",
     "https://example.com/docker-python"),
    ("Git and GitHub Crash Course",
     "Version control basics: commits, branches, pull requests, and GitHub Actions CI.",
     "https://example.com/git-github"),
    ("Data Engineering with pandas",
     "Data wrangling, cleaning, and feature engineering using pandas and NumPy.",
     "https://example.com/pandas-engineering"),
    ("PostgreSQL vs SQLite",
     "Choosing the right database: PostgreSQL for production, SQLite for local development.",
     "https://example.com/postgres-vs-sqlite"),
    ("Writing Unit Tests with pytest",
     "How to write clean, maintainable unit tests in Python using pytest and fixtures.",
     "https://example.com/pytest-guide"),
    ("Deploying FastAPI to AWS",
     "Step-by-step guide to deploying a FastAPI application on AWS EC2 and Lambda.",
     "https://example.com/fastapi-aws"),
]

QUERY_RELEVANCE = {
    "python tutorial":          [1, 2, 3],
    "fastapi":                  [3, 4, 15],
    "machine learning":         [6, 7, 8],
    "recommendation system":    [7, 8, 6],
    "rest api":                 [9, 3, 4],
    "database":                 [5, 13, 12],
    "docker":                   [10, 15, 3],
    "testing python":           [14, 2, 1],
    "data engineering":         [12, 5, 8],
    "git":                      [11, 14, 15],
}

def simulate_position_bias(position: int) -> float:
    """Simulate position bias: higher positions have higher click probabilities."""
    return 1.0/ (1 + 0.5 * (position-1))

def run(n_sessions: int = 300, seed: int=42):
    """ 
     We'll simulate 300 fake search sessions by default, but you can adjust this number as needed. 
     The seed parameter allows you to control the randomness for reproducibility.
    """
    random.seed(seed)
    # creating a table if one doesn't exist and then opening a database session
    init_db()
    db = SessionLocal()

    existing_urls = { r.url for r in db.query(SearchResult).all() }
    new_docs = []
    for title, content, url in DOCUMENTS:
        if url not in existing_urls:
            new_docs.append(SearchResult(title=title, content=content, url=url))
    
    if new_docs:
        db.add_all(new_docs)
        db.commit()
        print(f"Inserted {len(new_docs)} documents.")
    else:
        print("Documents already present, skipping")

    doc_map = {r.url: r.id for r in db.query(SearchResult).all()}
    doc_ids = list(doc_map.values())

    queries = list(QUERY_RELEVANCE.keys())
    impressions_to_add = []
    clicks_to_add = []

    for _ in range(n_sessions):
        # pick a random query and get the relevant document ids for that query
        query = random.choice(queries)

        # generating a unique session ID for this session
        session_id = str(uuid.uuid4())
        relevant_ids = QUERY_RELEVANCE[query]

        show_indices = random.sample(range(len(DOCUMENTS)),  5)
        # converting to 0-based indices as the relevance lists are 1-based
        rel_idx = random.choice(relevant_ids) - 1

        # ensuring at least one relevant document is shown in the results
        if rel_idx not in show_indices:
            show_indices[0] = rel_idx

        #  spreads fake sessions randomly across the past 30 days. This gives our recency scorer something meaningful to work with.
        ts = datetime.utcnow() - timedelta(minutes = random.randint(0, 43200))

        for pos, doc_idx in enumerate(show_indices, start=1):
            url = DOCUMENTS[doc_idx][2]
            result_id = doc_map[url] #type: ignore
            impressions_to_add.append(Impression(
                query=query,
                result_id=result_id,
                position=pos,
                session_id=session_id,
                timestamp=ts
            ))

            is_relevant = (doc_idx +  1) in relevant_ids
            # relevant results get 40% base click chance, irrelevant get 5% (noise)
            base_prop = 0.4 if is_relevant else 0.05
            # multiply by position bias so higher positions get clicked more often
            click_prob = base_prop * simulate_position_bias(pos)

            #  generates a number between 0 and 1. If it's less than click_prob, the user "clicked" on that result, and we create a ClickEvent for it.
            if random.random() < click_prob:
                clicks_to_add.append(ClickEvent(
                    query=query,
                    result_id=result_id,
                    position=pos,
                    session_id=session_id,
                    timestamp=ts ))
    
    db.add_all(impressions_to_add)
    db.add_all(clicks_to_add)
    db.commit()
    db.close()

    print(f"Simulated {n_sessions} sessions → "
          f"{len(impressions_to_add)} impressions, {len(clicks_to_add)} clicks.")

if __name__ == "__main__":
    run()
                




