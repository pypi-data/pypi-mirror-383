import time
import pytest
from terminal_monkeytype.main import Session

def test_session_word_count():
    session = Session(num_words=10)
    assert len(session.target_words) == 10

def test_session_target_text():
    session = Session(num_words=5)
    target = session.target_text
    assert isinstance(target, str)
    assert len(target.split()) == 5

def test_update_stats_no_typing():
    session = Session(num_words=5)
    session.start_time = time.time()
    wpm, acc, elapsed = session.update_stats()
    assert wpm == 0.0
    assert acc == 100.0

def test_update_stats_typing_correct():
    session = Session(num_words=5)
    session.target_words = ["hello", "world"]
    session.typed_chars = list("hello world")
    session.total_typed = len(session.typed_chars)
    session.correct_chars = len(session.typed_chars)
    session.start_time = time.time() - 60  # 1 minute elapsed
    wpm, acc, elapsed = session.update_stats()
    assert int(wpm) == len(session.typed_chars) // 5
    assert acc == 100.0

def test_mistakes_count():
    session = Session(num_words=1)
    session.target_words = ["abc"]
    session.typed_chars = list("abd")
    session.total_typed = len(session.typed_chars)
    session.correct_chars = sum(
        1 for i, c in enumerate(session.typed_chars) if i < len(session.target_text) and c == session.target_text[i]
    )
    session.mistakes = session.total_typed - session.correct_chars
    assert session.mistakes == 1