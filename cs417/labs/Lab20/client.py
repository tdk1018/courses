"""Lab 20: Build the Other Side — Client

Client functions that talk to your FastAPI server. Each task adds
a new function that handles a more realistic scenario.
"""

import requests
import time


def submit(student: str, lab: int, base_url: str = "http://localhost:8000") -> dict:
    """Task 1: Submit a grading request and return the result.

    POST to {base_url}/grade with {"student": student, "lab": lab}.
    Raise RuntimeError if the status code is not 200.
    Return the response as a dictionary.
    """
    # TODO: Implement
    pass


def submit_with_retry(
    student: str,
    lab: int,
    base_url: str = "http://localhost:8000",
    timeout: float = 2,
    max_retries: int = 3,
) -> dict:
    """Task 2: Submit with timeout and retry logic.

    POST to /grade with {"student": student, "lab": lab, "slow": True}.
    Use the timeout parameter in requests.post().
    On requests.exceptions.Timeout, retry up to max_retries times.
    Raise RuntimeError("all retries failed") if every attempt times out.
    Return the response dictionary on success.
    """
    # TODO: Implement
    pass


def submit_idempotent(
    student: str,
    lab: int,
    base_url: str = "http://localhost:8000",
    timeout: float = 2,
    max_retries: int = 3,
) -> dict:
    """Task 3: Submit with an idempotency key.

    Same as submit_with_retry, but include a stable submission_id
    in the request body: f"{student}-lab{lab}"
    """
    # TODO: Implement
    pass


def submit_async(
    student: str,
    lab: int,
    base_url: str = "http://localhost:8000",
    poll_interval: float = 0.5,
    max_polls: int = 20,
) -> dict:
    """Task 4: Async submission with polling.

    POST to /grade-async with student, lab, and a stable submission_id.
    Expect a 202 response with a job_id.
    Poll GET /grade-jobs/{job_id} every poll_interval seconds.
    When status is "complete", return the result dictionary.
    Raise RuntimeError("polling timed out") if max_polls is exceeded.
    """
    # TODO: Implement
    pass


# ---------------------------------------------------------------------------
# Bonus Task 5: The Smart Client
# ---------------------------------------------------------------------------


class SmartClient:
    """A client that tries sync first and falls back to async.

    Usage:
        client = SmartClient(base_url="http://localhost:8000")
        result = client.submit("alice", 19)
    """

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 2):
        # TODO: Implement
        pass

    def submit(self, student: str, lab: int) -> dict:
        """Submit a grading request. Tries sync first, falls back to async."""
        # TODO: Implement
        pass
