import random
import uuid
from datetime import datetime, timedelta

from db.session import SessionLocal, init_db
from db.models import SearchResult, Impression, ClickEvent