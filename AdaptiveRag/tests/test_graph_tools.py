"""
Unit tests for routing/decision helper functions -- these are pure functions
over the GraphState dict and require no API keys or external services.
"""
from src.tools.graph_tools import grade_decision, route_decision, verify_decision, MAX_RETRIES


def test_route_decision_valid_routes():
    assert route_decision({"route": "index"}) == "index"
    assert route_decision({"route": "general"}) == "general"
    assert route_decision({"route": "search"}) == "search"


def test_route_decision_defaults_to_general_for_unknown_route():
    assert route_decision({"route": "not_a_real_route"}) == "general"
    assert route_decision({}) == "general"


def test_grade_decision_generates_when_relevant_docs_present():
    state = {"relevant_documents": ["some relevant text"], "retries": 0}
    assert grade_decision(state) == "generate"


def test_grade_decision_rewrites_when_no_relevant_docs_and_retries_remain():
    state = {"relevant_documents": [], "retries": 0}
    assert grade_decision(state) == "rewrite"


def test_grade_decision_falls_back_to_web_search_after_max_retries():
    state = {"relevant_documents": [], "retries": MAX_RETRIES}
    assert grade_decision(state) == "web_search"


def test_verify_decision_ends_when_grounded():
    assert verify_decision({"is_grounded": True, "retries": 0}) == "end"


def test_verify_decision_rewrites_when_not_grounded_and_retries_remain():
    assert verify_decision({"is_grounded": False, "retries": 0}) == "rewrite"


def test_verify_decision_ends_when_not_grounded_but_retries_exhausted():
    assert verify_decision({"is_grounded": False, "retries": MAX_RETRIES}) == "end"
