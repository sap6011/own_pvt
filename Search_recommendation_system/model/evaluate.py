import math
from collections import defaultdict
from db.session import SessionLocal, init_db
from db.models import SearchResult, ClickEvent
from model.scorer import rerank

def build_ground_truth(db) -> dict:
    clicks = db.query(ClickEvent).all()
    ground_truth = defaultdict(set)
    for c in clicks:
        ground_truth[c.query].add(c.result_id)
    return ground_truth

def precision_at_k(ranked_ids: list, relevant_ids: set, k: int) -> float:
    top_k = ranked_ids[:k]
    hits = sum(1 for rid in top_k if rid in relevant_ids)
    return hits / k

def dcg_at_k(ranked_ids: list, relevant_ids: set, k: int) -> float:
    dcg = 0.0
    for i, rid in enumerate(ranked_ids[:k], start=1):
        if rid in relevant_ids:
            dcg += 1.0 / math.log2(i + 1)
    return dcg
def ndcg_at_k(ranked_ids: list, relevant_ids: set, k: int) -> float:
    actual_dcg = dcg_at_k(ranked_ids, relevant_ids, k)
    ideal_ids = list(relevant_ids) + [x for x in ranked_ids if x not in relevant_ids]
    ideal_dcg = dcg_at_k(ideal_ids, relevant_ids, k)
    return actual_dcg / ideal_dcg if ideal_dcg > 0 else 0.0

def evaluate(k: int = 5):
    init_db()
    db = SessionLocal()

    ground_truth = build_ground_truth(db)
    all_results  = db.query(SearchResult).all()
    queries      = list(ground_truth.keys())

    if not queries:
        print("No click data found. Run `python -m pipeline.simulate` first.")
        return
    p_at_k_scores    = []
    ndcg_at_k_scores = []

    print(f"\n{'Query':<30} {'P@'+str(k):<10} {'NDCG@'+str(k):<10} {'#Relevant'}")
    print("-" * 65)

    