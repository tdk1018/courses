"""Tests for Task 1: The Naive Server."""

import pytest
from fastapi.testclient import TestClient
from server import app


@pytest.fixture
def api():
    return TestClient(app)


class TestGradeEndpoint:
    """Test the POST /grade endpoint."""

    def test_returns_200(self, api):
        r = api.post("/grade", json={"student": "alice", "lab": 19})
        assert r.status_code == 200

    def test_response_has_student(self, api):
        data = api.post("/grade", json={"student": "alice", "lab": 19}).json()
        assert data["student"] == "alice"

    def test_response_has_lab(self, api):
        data = api.post("/grade", json={"student": "alice", "lab": 19}).json()
        assert data["lab"] == 19

    def test_response_has_score(self, api):
        data = api.post("/grade", json={"student": "alice", "lab": 19}).json()
        assert "score" in data
        assert isinstance(data["score"], int)
        assert 0 <= data["score"] <= 100

    def test_scores_are_deterministic(self, api):
        """Same student + same lab = same score every time."""
        s1 = api.post("/grade", json={"student": "alice", "lab": 19}).json()["score"]
        s2 = api.post("/grade", json={"student": "alice", "lab": 19}).json()["score"]
        assert s1 == s2

    def test_different_students_get_different_scores(self, api):
        s1 = api.post("/grade", json={"student": "alice", "lab": 19}).json()["score"]
        s2 = api.post("/grade", json={"student": "bob", "lab": 19}).json()["score"]
        assert s1 != s2


class TestSubmitClient:
    """Test the submit() client function."""

    def test_submit_returns_dict_with_score(self):
        from unittest.mock import patch, MagicMock
        from client import submit

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"student": "alice", "lab": 19, "score": 42}

        with patch("client.requests.post", return_value=mock_resp):
            result = submit("alice", 19)

        assert result["score"] == 42
        assert result["student"] == "alice"

    def test_submit_raises_on_error_status(self):
        from unittest.mock import patch, MagicMock
        from client import submit

        mock_resp = MagicMock()
        mock_resp.status_code = 500

        with patch("client.requests.post", return_value=mock_resp):
            with pytest.raises(RuntimeError):
                submit("alice", 19)
