"""Lab 20: Build the Other Side — Server

Your FastAPI grading server. Build each section as you work
through the tasks. The TODOs tell you what to add and where.
"""

from fastapi import FastAPI

app = FastAPI()


# ---------------------------------------------------------------------------
# Task 1: The Naive Server
# ---------------------------------------------------------------------------
# Import the grade function from grading.py, then create a POST /grade
# endpoint that accepts {"student": ..., "lab": ...} and returns the score.

# TODO: import grade from grading

# TODO: POST /grade endpoint


# ---------------------------------------------------------------------------
# Task 2: Retries Reveal a Problem
# ---------------------------------------------------------------------------
# Add a grading_log list that records every grading event.
# Update POST /grade to (1) accept an optional "slow" field and pass it
# to grade(), and (2) append each grading event to the log.
# Add GET /log and POST /reset-log endpoints.

# TODO: grading_log = []

# TODO: update POST /grade to log events and support "slow"

# TODO: GET /log endpoint

# TODO: POST /reset-log endpoint


# ---------------------------------------------------------------------------
# Task 3: Idempotency Makes Retries Safe
# ---------------------------------------------------------------------------
# Add a completed dict that maps submission IDs to results.
# Update POST /grade to check for an optional "submission_id" field —
# if the ID is already in completed, return the cached result without
# grading again or logging.
# Add POST /reset-completed endpoint.

# TODO: completed = {}

# TODO: update POST /grade to check submission_id

# TODO: POST /reset-completed endpoint


# ---------------------------------------------------------------------------
# Task 4: Honest About Time
# ---------------------------------------------------------------------------
# You'll need: from fastapi import BackgroundTasks
#              from fastapi.responses import JSONResponse
#
# Add jobs dict, job_submission_map dict, and a job ID generator.
# Create POST /grade-async (returns 202, runs grading in background).
# Create a run_grade_job helper that does the actual grading.
# Create GET /grade-jobs/{job_id} to check job status.

# TODO: jobs = {}
# TODO: job_submission_map = {}

# TODO: POST /grade-async endpoint

# TODO: run_grade_job helper function

# TODO: GET /grade-jobs/{job_id} endpoint
