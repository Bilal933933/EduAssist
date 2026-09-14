import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from app.core.errors import AppError
from app.core.validation import (
    ensure_thread_exists,
    validate_grade,
    validate_question,
    validate_teacher_id,
    validate_thread_id,
    validate_title,
    validate_topic,
)


class _Store:
    def __init__(self, existing=(1,)):
        self._existing = set(existing)

    def thread_exists(self, tid):
        return tid in self._existing


def test_question_empty_and_punct():
    for bad in ["", "   ", "؟؟؟", "??", "..."]:
        with pytest.raises(AppError) as e:
            validate_question(bad)
        assert e.value.code == "QUESTION_EMPTY"


def test_question_short_long():
    with pytest.raises(AppError) as e:
        validate_question("س")
    assert e.value.code == "QUESTION_TOO_SHORT"
    with pytest.raises(AppError) as e:
        validate_question("س" * 2001)
    assert e.value.code == "QUESTION_TOO_LONG"
    assert validate_question("  حضر درس الفاعل  ") == "حضر درس الفاعل"


def test_topic_teacher_title():
    assert validate_topic(" الفاعل ") == "الفاعل"
    with pytest.raises(AppError):
        validate_topic("  ")
    assert validate_teacher_id(None) == "default"
    with pytest.raises(AppError) as e:
        validate_teacher_id("bad id!")
    assert e.value.code == "TEACHER_ID_INVALID"
    assert validate_title(None) is None
    with pytest.raises(AppError) as e:
        validate_title("x" * 121)
    assert e.value.code == "TITLE_TOO_LONG"


def test_thread_and_grade():
    assert validate_thread_id(None) is None
    with pytest.raises(AppError):
        validate_thread_id(0)
    with pytest.raises(AppError):
        validate_thread_id(-3)
    ensure_thread_exists(_Store(), 1)
    with pytest.raises(AppError) as e:
        ensure_thread_exists(_Store(), 999)
    assert e.value.code == "THREAD_NOT_FOUND"
    assert validate_grade(None) is None
    assert validate_grade("grade5", catalog=["grade5"]) == "grade5"
    with pytest.raises(AppError) as e:
        validate_grade("unknown", catalog=["grade5"])
    assert e.value.code == "GRADE_UNKNOWN"
