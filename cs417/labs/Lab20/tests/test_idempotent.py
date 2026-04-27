"""Tests for Task 3: Idempotency Makes Retries Safe."""

import pytest
from fastapi.testclient import TestClient
from server import app


@pytest.fixture
def api():
    """Fresh test client with clean state."""
    client = TestClient(app)
    client.post("/reset-log")
    client.post("/reset-completed")
    return client


class TestIdempotency:
    """Test that submission_id prevents duplicate grading."""

    def test_same_id_grades_once(self, api):
        """The core test: same submission_id = one grading event,
        no matter how many requests the client sends."""
        for _ in range(3):
            api.post("/grade", json={
                "student": "alice", "lab": 19,
                "submission_id": "alice-lab19",
            })
        entries = api.get("/log").json()["entries"]
        assert len(entries) == 1

    def test_cached_result_matches_original(self, api):
        """The second response should be identical to the first."""
        payload = {"student": "alice", "lab": 19, "submission_id": "alice-lab19"}
        r1 = api.post("/grade", json=payload).json()
        r2 = api.post("/grade", json=payload).json()
        assert r1 == r2

    def test_different_ids_grade_separately(self, api):
        """Different submission IDs are treated as different submissions."""
        api.post("/grade", json={
            "student": "alice", "lab": 19,
            "submission_id": "alice-lab19",
        })
        api.post("/grade", json={
            "student": "bob", "lab": 19,
            "submission_id": "bob-lab19",
        })
        entries = api.get("/log").json()["entries"]
        assert len(entries) == 2

    def test_no_submission_id_still_works(self, api):
        """Requests without submission_id work like before — no caching."""
        api.post("/grade", json={"student": "alice", "lab": 19})
        api.post("/grade", json={"student": "alice", "lab": 19})
        entries = api.get("/log").json()["entries"]
        assert len(entries) == 2

    def test_reset_completed_clears_cache(self, api):
        """After clearing the cache, the same ID triggers a fresh grade."""
        api.post("/grade", json={
            "student": "alice", "lab": 19,
            "submission_id": "alice-lab19",
        })
        api.post("/reset-completed")
        api.post("/grade", json={
            "student": "alice", "lab": 19,
            "submission_id": "alice-lab19",
        })
        entries = api.get("/log").json()["entries"]
        assert len(entries) == 2


class TestIdempotentClient:
    """Test the submit_idempotent() client function."""

    def test_includes_submission_id(self):
        """submit_idempotent should include submission_id in the request."""
        from unittest.mock import patch, MagicMock
        from client import submit_idempotent

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"student": "alice", "lab": 19, "score": 42}

        with patch("client.requests.post", return_value=mock_resp) as mock_post:
            submit_idempotent("alice", 19)

        # Check that submission_id was in the posted JSON
        call_kwargs = mock_post.call_args
        sent_json = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert "submission_id" in sent_json
        assert sent_json["submission_id"] == "alice-lab19"
