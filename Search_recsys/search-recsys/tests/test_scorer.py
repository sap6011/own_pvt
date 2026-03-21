"""
tests/test_scorer.py
--------------------
Unit tests for the scoring and feature pipeline.

Run:
    pytest tests/ -v
"""

import pytest
from unittest.mock import MagicMock
from model.scorer import tfidf_similarity, _normalize, rerank
from pipeline.features import position_bias_correction


# ---- _normalize ---- #

def test_normalize_basic():
    result = _normalize([0.0, 0.5, 1.0])
    assert result == pytest.approx([0.0, 0.5, 1.0])


def test_normalize_all_equal():
    result = _normalize([3.0, 3.0, 3.0])
    assert result == [0.0, 0.0, 0.0]


def test_normalize_single():
    result = _normalize([5.0])
    assert result == [0.0]


# ---- tfidf_similarity ---- #

def test_tfidf_similarity_exact_match():
    sims = tfidf_similarity("python tutorial", ["python tutorial guide", "cooking recipes"])
    assert sims[0] > sims[1], "More similar doc should score higher"


def test_tfidf_similarity_no_docs():
    assert tfidf_similarity("anything", []) == []


def test_tfidf_similarity_returns_correct_length():
    docs = ["doc one", "doc two", "doc three"]
    sims = tfidf_similarity("one", docs)
    assert len(sims) == 3


# ---- position_bias_correction ---- #

def test_position_bias_decreases_with_rank():
    bias_1 = position_bias_correction(1)
    bias_5 = position_bias_correction(5)
    assert bias_1 > bias_5


def test_position_bias_position_one_is_max():
    assert position_bias_correction(1) == pytest.approx(1.0)


# ---- rerank (integration-style with mocked DB) ---- #

def make_mock_result(id, title, content, url=None):
    r = MagicMock()
    r.id = id
    r.title = title
    r.content = content
    r.url = url or f"https://example.com/{id}"
    return r


def test_rerank_returns_sorted_by_score():
    results = [
        make_mock_result(1, "Python tutorial", "Learn Python from scratch"),
        make_mock_result(2, "Cooking pasta", "How to cook perfect pasta"),
    ]
    db = MagicMock()
    # Mock get_all_features to return zeros (no click data)
    db.query.return_value.filter.return_value.all.return_value = []

    ranked = rerank("python", results, db)
    assert ranked[0]["id"] == 1, "Python doc should rank first for 'python' query"


def test_rerank_empty_results():
    db = MagicMock()
    assert rerank("python", [], db) == []


def test_rerank_score_between_0_and_1():
    results = [make_mock_result(1, "Python", "Python programming tutorial")]
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = []

    ranked = rerank("python", results, db)
    assert 0.0 <= ranked[0]["score"] <= 1.0
