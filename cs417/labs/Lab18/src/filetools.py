"""
Lab 18: Working with CSV and JSON Files

Read, write, and convert between CSV and JSON formats.
"""

import csv
import json
from pathlib import Path


def read_csv(filepath: str) -> list[dict]:
    """Read a CSV file and return a list of dictionaries.

    Each dictionary represents one row, with column headers as keys.

    TODO (Task 1):
    - Open the file with encoding="utf-8"
    - Use csv.DictReader to parse the rows
    - Return a list of all row dictionaries

    Args:
        filepath: Path to the CSV file.

    Returns:
        List of dicts, one per row.

    Example:
        >>> rows = read_csv("data/roster.csv")
        >>> rows[0]["name"]
        'Alice'
    """
    # TODO: Implement this function
    pass


def read_json(filepath: str):
    """Read a JSON file and return the parsed Python object.

    TODO (Task 2):
    - Open the file with encoding="utf-8"
    - Use json.load() to parse it
    - Return the result

    Args:
        filepath: Path to the JSON file.

    Returns:
        The parsed JSON data (usually a list or dict).

    Example:
        >>> data = read_json("data/roster.json")
        >>> data[0]["grade"]
        92
    """
    # TODO: Implement this function
    pass


def write_csv(filepath: str, data: list[dict], fieldnames: list[str]) -> None:
    """Write a list of dictionaries to a CSV file.

    TODO (Task 3):
    - Open the file in write mode with encoding="utf-8" and newline=""
    - Create a csv.DictWriter with the given fieldnames
    - Write the header row first
    - Write all data rows

    Args:
        filepath: Path for the output CSV file.
        data: List of dicts to write (one dict per row).
        fieldnames: Column names, in order.

    Example:
        >>> write_csv("output.csv", [{"name": "Alice", "grade": 92}], ["name", "grade"])
    """
    # TODO: Implement this function
    pass


def write_json(filepath: str, data) -> None:
    """Write a Python object to a JSON file with readable formatting.

    TODO (Task 4):
    - Open the file in write mode with encoding="utf-8"
    - Use json.dump() with indent=2 for readability
    - Set ensure_ascii=False so accented characters render correctly

    Args:
        filepath: Path for the output JSON file.
        data: The Python object to serialize.

    Example:
        >>> write_json("output.json", [{"name": "José", "grade": 91}])
    """
    # TODO: Implement this function
    pass


def csv_to_json(
    csv_path: str,
    json_path: str,
    type_hints: dict[str, type] | None = None,
) -> None:
    """Convert a CSV file to a JSON file.

    CSV stores everything as strings. The type_hints parameter lets you
    specify which columns should be converted to other types before
    writing JSON.

    TODO (Task 5a):
    - Read the CSV file using your read_csv function
    - For each row, convert values according to type_hints
      (e.g., if type_hints={"grade": int}, convert row["grade"] to int)
    - Write the result using your write_json function

    Args:
        csv_path: Path to the input CSV file.
        json_path: Path for the output JSON file.
        type_hints: Optional dict mapping column names to types.
                    Example: {"grade": int, "gpa": float}

    Example:
        >>> csv_to_json("roster.csv", "roster.json", type_hints={"grade": int})
    """
    # TODO: Implement this function
    pass


def json_to_csv(
    json_path: str,
    csv_path: str,
    fieldnames: list[str],
) -> None:
    """Convert a JSON file to a CSV file.

    JSON can hold nested data that doesn't fit in flat CSV columns.
    Only the keys listed in fieldnames are included — nested or
    unlisted fields are silently skipped.

    TODO (Task 5b):
    - Read the JSON file using your read_json function
    - For each record, build a new dict with only the fieldnames keys
    - Write the result using your write_csv function

    Args:
        json_path: Path to the input JSON file.
        csv_path: Path for the output CSV file.
        fieldnames: Which top-level keys to include as columns.

    Example:
        >>> json_to_csv("roster.json", "roster.csv", ["name", "email", "grade"])
        # "tags" field from JSON is skipped — it can't be a flat CSV column
    """
    # TODO: Implement this function
    pass
