# Lab 18: Working with CSV and JSON Files

## Bridge from Lab 17

In Lab 17, you built a DAG scheduler that figured out task order from dependency relationships — all in memory. But real programs don't live in memory alone. Data comes *from* somewhere (a file, an API, a database) and results go *to* somewhere.

This lab focuses on the two most common text-based data formats you'll encounter: **CSV** and **JSON**. You'll read them, write them, and discover why choosing between them is a design decision, not a coin flip.

## Background: Two Formats, Two Worldviews

### CSV — Tabular Data

CSV (Comma-Separated Values) stores data as a flat table. Every row has the same columns. Think spreadsheet.

```
name,email,grade
Alice,alice@uni.edu,92
Bob,bob@uni.edu,85
```

Rules:
- First row is usually the **header** (column names)
- Each subsequent row is one **record**
- Fields are separated by commas (the **delimiter**)
- If a field contains a comma, it gets wrapped in quotes: `"Portland, OR"`

Python's `csv` module handles the quoting rules so you don't have to.

### JSON — Structured Data

JSON (JavaScript Object Notation) stores data as nested structures — dictionaries and lists. It can represent things CSV can't: a student who has multiple phone numbers, a course with a list of prerequisites, a config file with nested settings.

```json
{
  "name": "Alice",
  "email": "alice@uni.edu",
  "grades": [92, 88, 95],
  "address": {
    "city": "Portland",
    "state": "OR"
  }
}
```

JSON maps directly to Python's `dict` and `list` types. `json.load()` gives you back exactly the structure you'd build by hand.

### When to Use Which

| Question | CSV | JSON |
|----------|-----|------|
| Is the data flat (same columns every row)? | Yes — CSV is natural | Works, but overkill |
| Does the data have nesting or variable structure? | Painful — you have to flatten | Yes — JSON handles this |
| Do you need to open it in Excel? | CSV opens directly | Not without conversion |
| Are you exchanging data with a web API? | Unusual | JSON is the standard |

The key insight: **format choice depends on the shape of your data**, not personal preference.

## Your Task

You'll build a small data pipeline that works with a roster of students. The data exists in two forms — a CSV file and a JSON file — and your code will read, transform, and write both.

### Starter Files

```
Lab18/
├── conftest.py          # Path setup for tests
├── data/
│   ├── roster.csv       # Student roster (tabular)
│   └── roster.json      # Student roster (structured)
├── src/
│   └── filetools.py     # Your implementations go here
└── tests/
    └── test_filetools.py
```

## Task 1: Read a CSV File

Open `src/filetools.py`. Find `read_csv`.

This function takes a file path and returns a list of dictionaries — one dict per row, with column headers as keys. Python's `csv.DictReader` does most of the heavy lifting, but you need to:

1. Open the file with the right encoding
2. Use `csv.DictReader` to parse it
3. Return a list of the row dictionaries

After this task, each row from `roster.csv` becomes a dictionary like:
```python
{"name": "Alice", "email": "alice@uni.edu", "grade": "92"}
```

Notice something: the grade is a **string**, not an integer. CSV doesn't know about types — everything is text. You'll deal with that later.

```bash
python -m pytest tests/ -k "test_read_csv" -v
git add -A && git commit -m "Lab 18: Implement read_csv"
```

## Task 2: Read a JSON File

Find `read_json` in `filetools.py`.

This function takes a file path and returns whatever Python object the JSON decodes to (usually a list or dict). Use `json.load()`.

Compare what you get back from `read_json("data/roster.json")` vs `read_csv("data/roster.csv")`. The JSON version preserves types — grades are integers, not strings. It can also hold nested data that CSV can't represent.

```bash
python -m pytest tests/ -k "test_read_json" -v
git add -A && git commit -m "Lab 18: Implement read_json"
```

## Task 3: Write a CSV File

Find `write_csv` in `filetools.py`.

This function takes a file path, a list of dictionaries, and a list of column names (fieldnames). It writes a CSV file with a header row and one data row per dictionary.

Things to get right:
- Open the file in write mode with `newline=""` (this prevents blank lines on Windows)
- Use `csv.DictWriter` with the provided fieldnames
- Write the header first, then the rows

```bash
python -m pytest tests/ -k "test_write_csv" -v
git add -A && git commit -m "Lab 18: Implement write_csv"
```

## Task 4: Write a JSON File

Find `write_json` in `filetools.py`.

This function takes a file path and a Python object, and writes it as formatted JSON. Use `json.dump()` with `indent=2` so the output is human-readable.

One detail: set `ensure_ascii=False` so names with accented characters (like "José") are written correctly instead of as escape sequences.

```bash
python -m pytest tests/ -k "test_write_json" -v
git add -A && git commit -m "Lab 18: Implement write_json"
```

## Task 5: Convert Between Formats

Find `csv_to_json` and `json_to_csv` in `filetools.py`.

This is where it gets interesting. You've now read and written both formats — but converting between them isn't just "load one, dump the other."

**`csv_to_json`**: Reads a CSV file and writes a JSON file. The catch — remember that CSV stores everything as strings. The `type_hints` parameter is a dictionary mapping column names to types (like `{"grade": int}`). Before writing JSON, convert the values for any column that has a type hint.

**`json_to_csv`**: Reads a JSON file and writes a CSV file. The catch — JSON can have nested data that doesn't fit in a flat CSV table. Your function receives a `fieldnames` list that specifies which top-level keys to include. Anything nested or unlisted simply gets skipped.

This is the central discovery of the lab: **conversion between formats isn't lossless.** Flattening JSON to CSV loses structure. Lifting CSV to JSON requires type information that CSV doesn't carry. Format choice matters.

```bash
python -m pytest tests/ -k "test_convert" -v
git add -A && git commit -m "Lab 18: Implement format conversion"
```

## Key Concepts

| Concept | What It Means |
|---------|--------------|
| CSV | Comma-separated values — flat tabular data, one record per row |
| JSON | JavaScript Object Notation — nested structured data |
| `csv.DictReader` | Reads CSV rows as dictionaries keyed by header names |
| `csv.DictWriter` | Writes dictionaries as CSV rows using specified fieldnames |
| `json.load()` / `json.dump()` | Read/write JSON from/to files |
| Type coercion | Converting string values to proper types (CSV doesn't preserve types) |
| Lossy conversion | Information lost when converting between formats with different capabilities |

## Running the Tests

```bash
cd Lab18
python -m pytest tests/ -v
```

Work through the tasks in order. Earlier tests will pass before later ones.
