"""
tests/test_mmr.py
-----------------
Tests unitaires pour l'algorithme MMR vectorisé.
"""

import numpy as np
from extraction import mmr_ranking


def test_mmr_empty():
    query = np.ones(200, dtype=np.float32)
    assert mmr_ranking(query, []) == []


def test_mmr_single_candidate():
    query = np.ones(200, dtype=np.float32)
    candidates = [{"file_path": "a.mp3", "vector": np.ones(200, dtype=np.float32)}]
    res = mmr_ranking(query, candidates)
    assert len(res) == 1
    assert res[0]["file_path"] == "a.mp3"


def test_mmr_k_param():
    np.random.seed(42)
    vecs = np.random.randn(10, 200).astype(np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    query = np.random.randn(200).astype(np.float32)
    query /= np.linalg.norm(query)
    candidates = [{"file_path": f"track_{i}.mp3", "vector": vecs[i]} for i in range(10)]

    # k=None -> all
    res_all = mmr_ranking(query, candidates, k=None)
    assert len(res_all) == 10

    # k=0 -> empty
    assert mmr_ranking(query, candidates, k=0) == []

    # k=3 -> top 3
    res_3 = mmr_ranking(query, candidates, k=3)
    assert len(res_3) == 3
    assert [c["file_path"] for c in res_3] == [c["file_path"] for c in res_all[:3]]

    # k > n -> all
    res_15 = mmr_ranking(query, candidates, k=15)
    assert len(res_15) == 10
    assert [c["file_path"] for c in res_15] == [c["file_path"] for c in res_all]


def test_mmr_lambda_extremes():
    np.random.seed(42)
    # Vecteur cible = [1, 0]
    query = np.array([1.0, 0.0], dtype=np.float32)
    # Candidat 1 : très similaire au query [1, 0]
    # Candidat 2 : identique au candidat 1 [1, 0]
    # Candidat 3 : orthogonal [0, 1]
    candidates = [
        {"file_path": "c1.mp3", "vector": np.array([1.0, 0.0], dtype=np.float32)},
        {"file_path": "c2.mp3", "vector": np.array([1.0, 0.0], dtype=np.float32)},
        {"file_path": "c3.mp3", "vector": np.array([0.0, 1.0], dtype=np.float32)},
    ]

    # lambda = 1.0 (pure pertinence) : c1 et c2 sont préférés à c3
    res_rel = mmr_ranking(query, candidates, lambda_param=1.0)
    paths_rel = [c["file_path"] for c in res_rel]
    assert paths_rel[2] == "c3.mp3"

    # lambda = 0.1 (forte diversité) : après c1, c3 (orthogonal) doit passer avant c2 (redondant)
    res_div = mmr_ranking(query, candidates, lambda_param=0.1)
    paths_div = [c["file_path"] for c in res_div]
    assert paths_div[0] in ("c1.mp3", "c2.mp3")
    assert paths_div[1] == "c3.mp3"
    assert paths_div[2] in ("c1.mp3", "c2.mp3")
