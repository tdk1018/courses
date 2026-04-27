"""Fake grading engine for Lab 20.

Produces deterministic scores from a hash so the lab can focus on
the API design, not the grading logic. Read this file before you
start — it's short and you'll need to understand what grade() does.
"""

import hashlib
import time


def grade(student: str, lab: int, slow: bool = False) -> int:
    """Grade a student's submission.

    Returns a deterministic score (0-100) based on the student name
    and lab number. The score comes from a hash, so the same inputs
    always produce the same output.

    If slow=True, simulates a long-running grading process (about 3
    seconds). You'll use this in Tasks 2-4 to explore what happens
    when the server takes a while to respond.
    """
    if slow:
        time.sleep(3)

    raw = f"{student}-lab{lab}"
    hash_val = int(hashlib.sha256(raw.encode()).hexdigest(), 16)
    return hash_val % 101  # Score between 0 and 100
