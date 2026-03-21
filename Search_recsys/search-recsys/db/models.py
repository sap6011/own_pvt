from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class SearchResult(Base):
    """A document/result that can be returned for queries."""
    __tablename__ = "search_results"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Impression(Base):
    """Logged every time a result is shown to a user."""
    __tablename__ = "impressions"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, nullable=False, index=True)
    result_id = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False)       # rank position shown (1-based)
    session_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class ClickEvent(Base):
    """Logged every time a user clicks a result."""
    __tablename__ = "click_events"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, nullable=False, index=True)
    result_id = Column(Integer, nullable=False, index=True)
    position = Column(Integer, nullable=False)       # position at time of click
    session_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
