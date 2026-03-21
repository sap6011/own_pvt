from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

DATABASE_URL = "sqlite:///./search_recommendation_system.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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