from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class SearchResult(Base):
    __tablename__ = 'search_results'

    id = Column(Integer, primary_key=True, indext=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Impression(Base):
    __tablename__ = 'impressions'

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, nullable=False)
    result_id = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False)
    session_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ClickEvent(Base):
    __tablename__ = 'click_events'

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, nullable=False, index=True)
    result_id = Column(Integer, nullable=False, index=True)
    position = Column(Integer, nullable=False)
    session_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    
   