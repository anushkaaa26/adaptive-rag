"""
Unit tests for shared utility functions.
"""
from src.tools.common_tools import format_docs, load_prompts, truncate


class _FakeDoc:
    def __init__(self, text):
        self.page_content = text


def test_format_docs_joins_document_objects():
    docs = [_FakeDoc("first chunk"), _FakeDoc("second chunk")]
    result = format_docs(docs)
    assert "first chunk" in result
    assert "second chunk" in result
    assert "---" in result


def test_format_docs_handles_plain_strings():
    result = format_docs(["just a string"])
    assert result == "just a string"


def test_truncate_short_text_unchanged():
    assert truncate("hello", max_chars=10) == "hello"


def test_truncate_long_text_is_cut_with_ellipsis():
    result = truncate("a" * 20, max_chars=5)
    assert result == "aaaaa..."


def test_load_prompts_contains_expected_keys():
    prompts = load_prompts()
    for key in ("system_prompt", "classify_prompt", "grading_prompt", "rewrite_prompt", "generate_prompt"):
        assert key in prompts
