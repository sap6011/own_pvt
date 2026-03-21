# Search Recommendation System

A production-style search reranking system that learns from user click behaviour.  
Built with **FastAPI**, **SQLAlchemy**, **scikit-learn**, and pure Python — no heavy ML frameworks required.

---

## How it works

```
score(result) = α × TF-IDF similarity
              + β × position-bias-corrected CTR
              + γ × recency-weighted click score
```

| Signal | What it captures |
|---|---|
| **TF-IDF similarity** | How well the result text matches the query |
| **Corrected CTR** | How often users click this result (debiased by position) |
| **Recency score** | Recent clicks weighted higher via exponential decay |

---

## Project structure

```
search-recsys/
├── api/
│   ├── main.py        ← FastAPI app + startup
│   ├── routes.py      ← /search, /recommend, /click, /impression, /stats
│   └── schemas.py     ← Pydantic request/response models
├── model/
│   ├── scorer.py      ← TF-IDF + CTR reranking logic
│   └── evaluate.py    ← Precision@K and NDCG@K offline evaluation
├── pipeline/
│   ├── simulate.py    ← Synthetic click data generator
│   └── features.py    ← CTR + recency feature computation
├── db/
│   ├── models.py      ← SQLAlchemy ORM models
│   └── session.py     ← DB engine, session, init
├── tests/
│   └── test_scorer.py ← Unit tests (pytest)
└── requirements.txt
```

---

## Quickstart

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate synthetic click data
```bash
python -m pipeline.simulate
```
This creates `search_recsys.db` with 15 documents and 300 simulated search sessions.

### 3. Start the API server
```bash
uvicorn api.main:app --reload
```
Open **http://localhost:8000/docs** for the interactive API explorer.

### 4. Try the endpoints

**Unranked search:**
```
GET http://localhost:8000/api/v1/search?q=python
```

**Reranked results:**
```
GET http://localhost:8000/api/v1/recommend?q=python&alpha=0.4&beta=0.4&gamma=0.2
```

**Log a click:**
```bash
curl -X POST http://localhost:8000/api/v1/click \
  -H "Content-Type: application/json" \
  -d '{"query": "python", "result_id": 1, "position": 2, "session_id": "abc123"}'
```

**System stats:**
```
GET http://localhost:8000/api/v1/stats
```

---

## Offline evaluation

```bash
python -m model.evaluate
```

Outputs **Precision@5** and **NDCG@5** for all queries — put these numbers on your resume.

---

## Run tests

```bash
pytest tests/ -v
```

---

## API reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/search` | Unranked keyword search |
| `GET` | `/api/v1/recommend` | **Reranked results** (main endpoint) |
| `POST` | `/api/v1/click` | Log a click event |
| `POST` | `/api/v1/impression` | Log an impression |
| `GET` | `/api/v1/stats` | System statistics |

### `/recommend` query parameters

| Param | Default | Description |
|---|---|---|
| `q` | required | Search query |
| `limit` | 10 | Number of results to return |
| `alpha` | 0.4 | Weight for TF-IDF text similarity |
| `beta` | 0.4 | Weight for corrected CTR |
| `gamma` | 0.2 | Weight for recency score |

---

## Resume bullets

> - Built an end-to-end search recommendation system using TF-IDF similarity and position-bias-corrected click-through rate signals, achieving NDCG@5 of **X.XXX**
> - Designed a data pipeline to ingest click events, compute recency-weighted CTR features, and correct for position bias in user click logs
> - Served real-time reranked search results via a FastAPI REST API backed by SQLAlchemy and SQLite/PostgreSQL
