"""Tests for Lab 18: Working with CSV and JSON Files."""

import csv
import json
from pathlib import Path

import pytest

from filetools import read_csv, read_json, write_csv, write_json, csv_to_json, json_to_csv

# Resolve the data directory relative to the lab root
LAB_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = LAB_ROOT / "data"


# ── Task 1: read_csv ──────────────────────────────────────────────


class TestReadCSV:
    """Tests for reading CSV files."""

    def test_read_csv_returns_list(self):
        result = read_csv(str(DATA_DIR / "roster.csv"))
        assert isinstance(result, list)

    def test_read_csv_row_count(self):
        result = read_csv(str(DATA_DIR / "roster.csv"))
        assert len(result) == 5

    def test_read_csv_first_row(self):
        result = read_csv(str(DATA_DIR / "roster.csv"))
        assert result[0]["name"] == "Alice"
        assert result[0]["email"] == "alice@uni.edu"
        assert result[0]["grade"] == "92"  # CSV values are strings

    def test_read_csv_all_rows_are_dicts(self):
        result = read_csv(str(DATA_DIR / "roster.csv"))
        for row in result:
            assert isinstance(row, dict)
            assert "name" in row
            assert "email" in row
            assert "grade" in row

    def test_read_csv_values_are_strings(self):
        """CSV doesn't preserve types — grades come back as strings."""
        result = read_csv(str(DATA_DIR / "roster.csv"))
        for row in result:
            assert isinstance(row["grade"], str)


# ── Task 2: read_json ─────────────────────────────────────────────


class TestReadJSON:
    """Tests for reading JSON files."""

    def test_read_json_returns_list(self):
        result = read_json(str(DATA_DIR / "roster.json"))
        assert isinstance(result, list)

    def test_read_json_row_count(self):
        result = read_json(str(DATA_DIR / "roster.json"))
        assert len(result) == 5

    def test_read_json_first_record(self):
        result = read_json(str(DATA_DIR / "roster.json"))
        assert result[0]["name"] == "Alice"
        assert result[0]["email"] == "alice@uni.edu"
        assert result[0]["grade"] == 92  # JSON preserves int type

    def test_read_json_preserves_types(self):
        """JSON knows the difference between 92 and '92'."""
        result = read_json(str(DATA_DIR / "roster.json"))
        for record in result:
            assert isinstance(record["grade"], int)

    def test_read_json_nested_data(self):
        """JSON can hold lists inside records — CSV can't."""
        result = read_json(str(DATA_DIR / "roster.json"))
        assert isinstance(result[0]["tags"], list)
        assert "dean_list" in result[0]["tags"]


# ── Task 3: write_csv ─────────────────────────────────────────────


class TestWriteCSV:
    """Tests for writing CSV files."""

    def test_write_csv_creates_file(self, tmp_path):
        outfile = str(tmp_path / "out.csv")
        data = [{"name": "Alice", "grade": "92"}]
        write_csv(outfile, data, ["name", "grade"])
        assert Path(outfile).exists()

    def test_write_csv_has_header(self, tmp_path):
        outfile = str(tmp_path / "out.csv")
        data = [{"name": "Alice", "grade": "92"}]
        write_csv(outfile, data, ["name", "grade"])
        with open(outfile, encoding="utf-8") as f:
            header = f.readline().strip()
        assert header == "name,grade"

    def test_write_csv_has_data_rows(self, tmp_path):
        outfile = str(tmp_path / "out.csv")
        data = [
            {"name": "Alice", "grade": "92"},
            {"name": "Bob", "grade": "85"},
        ]
        write_csv(outfile, data, ["name", "grade"])
        with open(outfile, encoding="utf-8") as f:
            lines = f.read().strip().split("\n")
        assert len(lines) == 3  # header + 2 data rows

    def test_write_csv_roundtrip(self, tmp_path):
        """Write then read back — data should survive the trip."""
        outfile = str(tmp_path / "roundtrip.csv")
        original = read_csv(str(DATA_DIR / "roster.csv"))
        write_csv(outfile, original, ["name", "email", "grade"])
        reloaded = read_csv(outfile)
        assert len(reloaded) == len(original)
        for orig, new in zip(original, reloaded):
            assert orig["name"] == new["name"]
            assert orig["email"] == new["email"]
            assert orig["grade"] == new["grade"]

    def test_write_csv_respects_fieldname_order(self, tmp_path):
        outfile = str(tmp_path / "ordered.csv")
        data = [{"grade": "92", "name": "Alice"}]
        write_csv(outfile, data, ["grade", "name"])  # grade first
        with open(outfile, encoding="utf-8") as f:
            header = f.readline().strip()
        assert header == "grade,name"


# ── Task 4: write_json ────────────────────────────────────────────


class TestWriteJSON:
    """Tests for writing JSON files."""

    def test_write_json_creates_file(self, tmp_path):
        outfile = str(tmp_path / "out.json")
        write_json(outfile, [{"name": "Alice"}])
        assert Path(outfile).exists()

    def test_write_json_valid_json(self, tmp_path):
        outfile = str(tmp_path / "out.json")
        data = [{"name": "Alice", "grade": 92}]
        write_json(outfile, data)
        with open(outfile, encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded == data

    def test_write_json_is_formatted(self, tmp_path):
        """Output should be indented, not a single line."""
        outfile = str(tmp_path / "out.json")
        write_json(outfile, [{"name": "Alice"}])
        with open(outfile, encoding="utf-8") as f:
            text = f.read()
        assert "\n" in text  # indented output has newlines

    def test_write_json_handles_unicode(self, tmp_path):
        """Accented characters should appear as-is, not as escape sequences."""
        outfile = str(tmp_path / "unicode.json")
        write_json(outfile, [{"name": "José"}])
        with open(outfile, encoding="utf-8") as f:
            text = f.read()
        assert "José" in text  # not \\u00e9

    def test_write_json_roundtrip(self, tmp_path):
        """Write then read back — data should survive the trip."""
        outfile = str(tmp_path / "roundtrip.json")
        original = read_json(str(DATA_DIR / "roster.json"))
        assert original is not None, "read_json must be implemented first"
        write_json(outfile, original)
        reloaded = read_json(outfile)
        assert reloaded is not None
        assert reloaded == original


# ── Task 5: Format conversion ─────────────────────────────────────


class TestConvert:
    """Tests for converting between CSV and JSON."""

    def test_csv_to_json_basic(self, tmp_path):
        outfile = str(tmp_path / "converted.json")
        csv_to_json(str(DATA_DIR / "roster.csv"), outfile)
        result = read_json(outfile)
        assert len(result) == 5
        assert result[0]["name"] == "Alice"

    def test_csv_to_json_without_hints_keeps_strings(self, tmp_path):
        """Without type hints, grades stay as strings."""
        outfile = str(tmp_path / "no_hints.json")
        csv_to_json(str(DATA_DIR / "roster.csv"), outfile)
        result = read_json(outfile)
        assert result[0]["grade"] == "92"  # still a string

    def test_csv_to_json_with_type_hints(self, tmp_path):
        """Type hints convert string values to proper types."""
        outfile = str(tmp_path / "typed.json")
        csv_to_json(
            str(DATA_DIR / "roster.csv"),
            outfile,
            type_hints={"grade": int},
        )
        result = read_json(outfile)
        assert result[0]["grade"] == 92  # now an int
        assert isinstance(result[0]["grade"], int)

    def test_json_to_csv_basic(self, tmp_path):
        outfile = str(tmp_path / "converted.csv")
        json_to_csv(
            str(DATA_DIR / "roster.json"),
            outfile,
            fieldnames=["name", "email", "grade"],
        )
        result = read_csv(outfile)
        assert len(result) == 5
        assert result[0]["name"] == "Alice"

    def test_json_to_csv_drops_nested_fields(self, tmp_path):
        """Nested fields like 'tags' should be skipped, not crash."""
        outfile = str(tmp_path / "flat.csv")
        json_to_csv(
            str(DATA_DIR / "roster.json"),
            outfile,
            fieldnames=["name", "email", "grade"],
        )
        result = read_csv(outfile)
        # "tags" was in JSON but not in fieldnames — should be gone
        for row in result:
            assert "tags" not in row

    def test_json_to_csv_grade_becomes_string(self, tmp_path):
        """JSON int grades become CSV strings — that's expected."""
        outfile = str(tmp_path / "stringified.csv")
        json_to_csv(
            str(DATA_DIR / "roster.json"),
            outfile,
            fieldnames=["name", "email", "grade"],
        )
        result = read_csv(outfile)
        # CSV always gives strings back
        assert isinstance(result[0]["grade"], str)
