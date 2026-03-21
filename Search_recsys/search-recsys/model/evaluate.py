"""
evaluate.py
-----------
Offline evaluation of the reranker using held-out click data.

Metrics
-------
Precision@K  : fraction of top-K results that were ever clicked
NDCG@K       : normalized discounted cumulative gain — rewards relevant
               results ranked higher

Run:
    python -m model.evaluate
"""

import math
from collections import defaultdict
from db.session import SessionLocal, init_db
from db.models import SearchResult, ClickEvent, Impression
from model.scorer import rerank


# ---- Ground truth: result_ids that were clicked for each query ---- #
def build_ground_truth(db) -> dict[str, set[int]]:
    clicks = db.query(ClickEvent).all()
    ground_truth = defaultdict(set)
    for c in clicks:
        ground_truth[c.query].add(c.result_id)
    return ground_truth


def precision_at_k(ranked_ids: list[int], relevant_ids: set[int], k: int) -> float:
    top_k = ranked_ids[:k]
    hits = sum(1 for rid in top_k if rid in relevant_ids)
    return hits / k


def dcg_at_k(ranked_ids: list[int], relevant_ids: set[int], k: int) -> float:
    dcg = 0.0
    for i, rid in enumerate(ranked_ids[:k], start=1):
        if rid in relevant_ids:
            dcg += 1.0 / math.log2(i + 1)
    return dcg


def ndcg_at_k(ranked_ids: list[int], relevant_ids: set[int], k: int) -> float:
    actual_dcg = dcg_at_k(ranked_ids, relevant_ids, k)
    # Ideal: all relevant docs ranked first
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

    for query in sorted(queries):
        relevant_ids = ground_truth[query]

        # Rerank all documents for this query
        ranked = rerank(query, all_results, db)
        ranked_ids = [r["id"] for r in ranked]

        p    = precision_at_k(ranked_ids, relevant_ids, k)
        ndcg = ndcg_at_k(ranked_ids, relevant_ids, k)

        p_at_k_scores.append(p)
        ndcg_at_k_scores.append(ndcg)

        print(f"{query:<30} {p:<10.3f} {ndcg:<10.3f} {len(relevant_ids)}")

    avg_p    = sum(p_at_k_scores)    / len(p_at_k_scores)
    avg_ndcg = sum(ndcg_at_k_scores) / len(ndcg_at_k_scores)

    print("-" * 65)
    print(f"{'AVERAGE':<30} {avg_p:<10.3f} {avg_ndcg:<10.3f}")
    print(f"\n✓ Mean Precision@{k}  : {avg_p:.3f}")
    print(f"✓ Mean NDCG@{k}      : {avg_ndcg:.3f}")
    print("\nThese numbers go on your resume! 🎉")

    db.close()
    return {"precision_at_k": avg_p, "ndcg_at_k": avg_ndcg}


if __name__ == "__main__":
    evaluate(k=5)
