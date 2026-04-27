"""Tests for Task 4: Honest About Time."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from server import app


@pytest.fixture
def api():
    """Fresh test client with clean state."""
    client = TestClient(app)
    client.post("/reset-log")
    client.post("/reset-completed")
    # Clear async state if it exists
    import server
    for attr in ("jobs", "job_submission_map"):
        store = getattr(server, attr, None)
        if store is not None:
            store.clear()
    return client


class TestAsyncGrading:
    """Test the POST /grade-async and GET /grade-jobs/{job_id} endpoints."""

    @patch("grading.time.sleep")  # Skip the 3-second sleep
    def test_returns_202(self, mock_sleep, api):
        r = api.post("/grade-async", json={"student": "alice", "lab": 19})
        assert r.status_code == 202

    @patch("grading.time.sleep")
    def test_returns_job_id(self, mock_sleep, api):
        data = api.post("/grade-async", json={"student": "alice", "lab": 19}).json()
        assert "job_id" in data
        assert data["status"] == "accepted"

    @patch("grading.time.sleep")
    def test_job_completes_with_result(self, mock_sleep, api):
        """After the background task runs, polling should return the result."""
        data = api.post("/grade-async", json={"student": "alice", "lab": 19}).json()
        job_id = data["job_id"]

        # In the test client, background tasks run before the next request
        status = api.get(f"/grade-jobs/{job_id}").json()
        assert status["status"] == "complete"
        assert status["result"]["student"] == "alice"
        assert isinstance(status["result"]["score"], int)

    @patch("grading.time.sleep")
    def test_result_score_is_valid(self, mock_sleep, api):
        data = api.post("/grade-async", json={"student": "alice", "lab": 19}).json()
        result = api.get(f"/grade-jobs/{data['job_id']}").json()["result"]
        assert 0 <= result["score"] <= 100

    def test_unknown_job_returns_404(self, api):
        r = api.get("/grade-jobs/nonexistent-id")
        assert r.status_code == 404

    @patch("grading.time.sleep")
    def test_idempotent_returns_same_job(self, mock_sleep, api):
        """Same submission_id should return the same job, not create a new one."""
        r1 = api.post("/grade-async", json={
            "student": "alice", "lab": 19,
            "submission_id": "alice-lab19",
        })
        r2 = api.post("/grade-async", json={
            "student": "alice", "lab": 19,
            "submission_id": "alice-lab19",
        })
        assert r1.json()["job_id"] == r2.json()["job_id"]

    @patch("grading.time.sleep")
    def test_async_logs_exactly_once(self, mock_sleep, api):
        """Async grading should create exactly one log entry."""
        data = api.post("/grade-async", json={
            "student": "alice", "lab": 19,
            "submission_id": "alice-lab19",
        }).json()
        # Trigger background task completion by making another request
        api.get(f"/grade-jobs/{data['job_id']}")
        entries = api.get("/log").json()["entries"]
        assert len(entries) == 1


class TestAsyncClient:
    """Test the submit_async() client function."""

    def test_polls_until_complete(self):
        """submit_async should POST, then poll until the job finishes."""
        from unittest.mock import patch as mock_patch, MagicMock
        from client import submit_async

        # Mock POST -> 202 with job_id
        post_resp = MagicMock()
        post_resp.status_code = 202
        post_resp.json.return_value = {"job_id": "j1", "status": "accepted"}

        # Mock GET -> pending once, then complete
        pending = MagicMock()
        pending.json.return_value = {"job_id": "j1", "status": "pending"}
        complete = MagicMock()
        complete.json.return_value = {
            "job_id": "j1",
            "status": "complete",
            "result": {"student": "alice", "lab": 19, "score": 85},
        }

        with mock_patch("client.requests.post", return_value=post_resp), \
             mock_patch("client.requests.get", side_effect=[pending, complete]), \
             mock_patch("client.time.sleep"):
            result = submit_async("alice", 19)

        assert result["score"] == 85

    def test_raises_on_non_202(self):
        """submit_async should raise if the server doesn't return 202."""
        from unittest.mock import patch as mock_patch, MagicMock
        from client import submit_async

        bad_resp = MagicMock()
        bad_resp.status_code = 500

        with mock_patch("client.requests.post", return_value=bad_resp):
            with pytest.raises(RuntimeError):
                submit_async("alice", 19)
