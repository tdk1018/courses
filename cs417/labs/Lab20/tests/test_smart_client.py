"""Bonus tests for Task 5: The Smart Client."""

import pytest
import requests as req
from unittest.mock import patch, MagicMock


class TestSmartClient:
    """Test the SmartClient class."""

    def test_sync_success_returns_immediately(self):
        """When the sync endpoint responds fast, SmartClient returns it."""
        from client import SmartClient

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"student": "alice", "lab": 19, "score": 85}

        with patch("client.requests.post", return_value=mock_resp):
            client = SmartClient()
            result = client.submit("alice", 19)

        assert result["score"] == 85

    def test_falls_back_to_async_on_timeout(self):
        """When sync times out, SmartClient falls back to async and polls."""
        from client import SmartClient

        call_count = {"n": 0}

        def mock_post(url, **kwargs):
            call_count["n"] += 1
            if "/grade-async" not in url:
                # Sync attempt — simulate timeout
                raise req.exceptions.Timeout()
            # Async attempt — return 202
            resp = MagicMock()
            resp.status_code = 202
            resp.json.return_value = {"job_id": "j1", "status": "accepted"}
            return resp

        def mock_get(url, **kwargs):
            resp = MagicMock()
            resp.json.return_value = {
                "job_id": "j1",
                "status": "complete",
                "result": {"student": "alice", "lab": 19, "score": 85},
            }
            return resp

        with patch("client.requests.post", side_effect=mock_post), \
             patch("client.requests.get", side_effect=mock_get), \
             patch("client.time.sleep"):
            client = SmartClient()
            result = client.submit("alice", 19)

        assert result["score"] == 85
