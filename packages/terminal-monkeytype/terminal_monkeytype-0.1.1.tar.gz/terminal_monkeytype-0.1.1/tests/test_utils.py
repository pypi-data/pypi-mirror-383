import os
import json
import tempfile
import pytest
from unittest.mock import patch
from terminal_monkeytype.main import save_result, load_leaderboard

@pytest.fixture
def temp_results_file():
    """Create a temporary results file and yield its path."""
    with tempfile.NamedTemporaryFile(delete=False, mode='w+', encoding='utf-8') as tmp:
        tmp.write("[]")  # start with empty JSON
        tmp.flush()
        yield tmp.name
    os.remove(tmp.name)

def test_save_and_load_results(temp_results_file):
    # Patch RESULTS_FILE to use temp file
    with patch("terminal_monkeytype.main.RESULTS_FILE", temp_results_file):
        save_result(60, 95.0, 25)
        results = load_leaderboard()
        assert len(results) == 1
        r = results[0]
        assert r["wpm"] == 60
        assert r["accuracy"] == 95.0
        assert r["words"] == 25

def test_save_multiple_results(temp_results_file):
    with patch("terminal_monkeytype.main.RESULTS_FILE", temp_results_file):
        # Add multiple results
        for i in range(55):  # test trimming to last 50
            save_result(i, 100 - i, i + 1)
        results = load_leaderboard()
        assert len(results) == 50  # should keep last 50
        # Check first and last entries
        assert results[0]["wpm"] == 5
        assert results[-1]["wpm"] == 54