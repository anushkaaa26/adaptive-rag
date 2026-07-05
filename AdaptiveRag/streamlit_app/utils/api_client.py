"""
Backend API client used by the Streamlit app to talk to the FastAPI service.
"""
import os

import requests

BASE_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
TIMEOUT = 60


def send_query(query: str, session_id: str) -> dict:
    resp = requests.post(
        f"{BASE_URL}/rag/query",
        json={"query": query, "session_id": session_id},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def upload_document(file_bytes: bytes, filename: str, description: str) -> dict:
    resp = requests.post(
        f"{BASE_URL}/rag/documents/upload",
        headers={"X-Description": description},
        files={"file": (filename, file_bytes)},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def get_history(session_id: str) -> dict:
    resp = requests.get(f"{BASE_URL}/rag/history/{session_id}", timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def check_health() -> bool:
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def register(username: str, password: str) -> tuple[bool, str]:
    try:
        resp = requests.post(
            f"{BASE_URL}/auth/register",
            json={"username": username, "password": password},
            timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            return True, resp.json().get("message", "Registered.")
        return False, resp.json().get("detail", "Registration failed.")
    except requests.RequestException as exc:
        return False, f"Could not reach backend: {exc}"


def login(username: str, password: str) -> tuple[bool, str]:
    try:
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            return True, resp.json().get("message", "Logged in.")
        return False, resp.json().get("detail", "Login failed.")
    except requests.RequestException as exc:
        return False, f"Could not reach backend: {exc}"
