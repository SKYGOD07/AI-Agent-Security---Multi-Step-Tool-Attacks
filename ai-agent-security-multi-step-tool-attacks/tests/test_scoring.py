import sys
from unittest.mock import MagicMock

# Mock broken aicomp_sdk dependencies so we can import scoring.py
sys.modules['aicomp_sdk.core.env'] = MagicMock()
sys.modules['aicomp_sdk.core.env.api'] = MagicMock()
sys.modules['aicomp_sdk.core.env.sandbox'] = MagicMock()
sys.modules['aicomp_sdk.core.env.gym'] = MagicMock()

from aicomp_sdk.scoring import get_score_cell_hash

def test_get_score_cell_hash_with_score_cell_signature():
    finding = {
        "score_cell_signature": {
            "hash": "hash_123"
        }
    }
    assert get_score_cell_hash(finding) == "hash_123"

def test_get_score_cell_hash_with_cell_signature():
    finding = {
        "cell_signature": {
            "hash": "hash_456"
        }
    }
    assert get_score_cell_hash(finding) == "hash_456"

def test_get_score_cell_hash_prefer_score_cell_signature():
    finding = {
        "score_cell_signature": {
            "hash": "hash_123"
        },
        "cell_signature": {
            "hash": "hash_456"
        }
    }
    assert get_score_cell_hash(finding) == "hash_123"

def test_get_score_cell_hash_missing_hash():
    finding = {
        "score_cell_signature": {}
    }
    assert get_score_cell_hash(finding) is None

def test_get_score_cell_hash_hash_not_string():
    finding = {
        "score_cell_signature": {
            "hash": 123
        }
    }
    assert get_score_cell_hash(finding) is None

def test_get_score_cell_hash_not_mapping():
    finding = {
        "score_cell_signature": "not_a_mapping"
    }
    assert get_score_cell_hash(finding) is None

def test_get_score_cell_hash_empty_finding():
    finding = {}
    assert get_score_cell_hash(finding) is None
