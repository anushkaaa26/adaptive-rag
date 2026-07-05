"""
Unit tests for Pydantic request/response models.
"""
import pytest
from pydantic import ValidationError

from src.models.grade import Grade
from src.models.query_request import QueryRequest
from src.models.route_identifier import RouteQuery
from src.models.user import UserCreate
from src.models.verification_result import VerificationResult


def test_query_request_requires_query_and_session_id():
    req = QueryRequest(query="hello", session_id="abc123")
    assert req.query == "hello"
    assert req.session_id == "abc123"

    with pytest.raises(ValidationError):
        QueryRequest(session_id="abc123")  # missing query


def test_route_query_accepts_only_known_literals():
    assert RouteQuery(route="index").route == "index"
    with pytest.raises(ValidationError):
        RouteQuery(route="not_a_route")


def test_grade_model():
    grade = Grade(binary_score="yes")
    assert grade.binary_score == "yes"


def test_verification_result_model():
    result = VerificationResult(is_grounded=False, reasoning="context did not mention this")
    assert result.is_grounded is False


def test_user_create_enforces_minimum_password_length():
    UserCreate(username="alice", password="longenough")
    with pytest.raises(ValidationError):
        UserCreate(username="alice", password="short")
