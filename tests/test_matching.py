# tests/test_matching.py
from job_hunter.matching.rank import _cosine

def test_cosine_monotonic():
    """Identical vectors should score higher than orthogonal ones."""
    assert _cosine([1, 0, 0], [1, 0, 0]) > _cosine([1, 0, 0], [0, 1, 0])