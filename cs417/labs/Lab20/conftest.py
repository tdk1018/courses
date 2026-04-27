"""Lab 20 test configuration."""

import sys
from pathlib import Path

# Add the Lab20 directory to the import path so tests can find
# server.py, client.py, and grading.py.
sys.path.insert(0, str(Path(__file__).parent))
