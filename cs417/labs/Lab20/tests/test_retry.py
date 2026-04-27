"""Tests for Task 2: Retries Reveal a Problem."""

import pytest
import requests as req
from fastapi.testclient import TestClient
from server import app


@pytest.fixture
def api():
    """Fresh test client with a clean log."""
    client = TestClient(app)
    client.post("/reset-log")
    return client


class TestGradingLog:
    """Test that the server logs every grading event."""

    def test_log_starts_empty(self, api):
        entries = api.get("/log").json()["entries"]
        assert entries == []

    def test_grading_adds_log_entry(self, api):
        api.post("/grade", json={"student": "alice", "lab": 19})
        entries = api.get("/log").json()["entries"]
        assert len(entries) == 1
        assert entries[0]["student"] == "alice"
        assert entries[0]["lab"] == 19

    def test_repeated_calls_create_duplicate_entries(self, api):
        """This is the key discovery: without idempotency, every
        request creates a new log entry — even for the same student
        and lab. Imagine each entry is a real grade being recorded."""
        for _ in range(3):
            api.post("/grade", json={"student": "alice", "lab": 19})
        entries = api.get("/log").json()["entries"]
        assert len(entries) == 3

    def test_reset_log_clears_entries(self, api):
        api.post("/grade", json={"student": "alice", "lab": 19})
        api.post("/reset-log")
        entries = api.get("/log").json()["entries"]
        assert entries == []


class TestSlowGrading:
    """Test that the server accepts the slow parameter."""

    def test_accepts_slow_field(self, api):
        """Server should accept slow=False without errors."""
        r = api.post("/grade", json={"student": "alice", "lab": 19, "slow": False})
        assert r.status_code == 200


class TestRetryClient:
    """Test the submit_with_retry() client function."""

    def test_raises_after_all_retries_fail(self):
        """If every attempt times out, submit_with_retry raises RuntimeError."""
        from unittest.mock import patch
        from client import submit_with_retry

        with patch("client.requests.post", side_effect=req.exceptions.Timeout):
            with pytest.raises(RuntimeError, match="all retries failed"):
                submit_with_retry("alice", 19, max_retries=3)

    def test_succeeds_on_second_attempt(self):
        """If the first call times out but the second succeeds, return the result."""
        from unittest.mock import patch, MagicMock
        from client import submit_with_retry

        good_resp = MagicMock()
        good_resp.status_code = 200
        good_resp.json.return_value = {"student": "alice", "lab": 19, "score": 42}

        # First call times out, second call succeeds
        with patch(
            "client.requests.post",
            side_effect=[req.exceptions.Timeout, good_resp],
        ):
            result = submit_with_retry("alice", 19, max_retries=3)

        assert result["score"] == 42
