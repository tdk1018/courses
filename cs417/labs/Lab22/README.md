# Lab 22: Trust but Verify — Reading Code You Didn't Write

## Overview

Most labs in this course have asked you to **write** code. This one asks you
to **read** it.

You will be given three solutions to the same problem — `solution_a.py`,
`solution_b.py`, `solution_c.py`. All three are correct. All three pass the
basic test suite. They could have been written by an AI assistant, by an
intern, by a senior engineer in a hurry, or by yesterday-you. The lab does not
tell you which, because in real engineering the source of the code is rarely
the most useful information about it.

Your job is to **rank them by quality** and **defend your ranking with
evidence**. That is most of what code review actually is. Real code review is
rarely *"this is broken"*; it is almost always *"this works, but…"*

This lab is mostly writing and thinking. You will not be writing implementations
of your own. You will be reading carefully, predicting, measuring, and arguing.

**Starter files:** `src/solution_a.py`, `src/solution_b.py`, `src/solution_c.py`,
`tests/test_basic.py`, `tests/test_hard.py`, `benchmark.py`, `requirements.txt`,
`rubric.md`

**Setup:**

```bash
pip install -r requirements.txt
pytest -v tests/test_basic.py
```

All 18 basic tests should pass on first run — you do not need to write any code.

## Background: The Problem

The three solutions all implement the same function:

```python
def top_k_frequent(items: list[str], k: int) -> list[tuple[str, int]]:
    """Return the k most frequent items in `items`, paired with their counts,
    ordered most-frequent-first. Ties broken by first-appearance order in `items`.
    """
```

In plain English: given a list of items, return the K items that show up most
often, paired with their counts, with the most frequent first. If two items
tied on count, the one that *first appeared* earlier in the input wins.

**Example:**
```python
top_k_frequent(["a", "b", "a", "c", "a", "b"], 2)
# → [("a", 3), ("b", 2)]
```

This problem comes up everywhere:

- Most-searched terms in a search log
- Hottest items in an inventory feed
- Most common words in a document
- Top error codes in a server log

It is also a problem with a **clean quality gradient**: there are several
correct ways to do it, and they differ a lot in performance, edge-case
handling, and clarity — without any of them being "wrong."

### What "first-appearance order" means for ties

If three items all have the same count, the one whose *first occurrence in the
input* came earliest is ranked first. So:

```python
items = ["b", "a", "c", "a", "b", "c"]   # a:2, b:2, c:2 — all tied
# First appearances: b at index 0, a at index 1, c at index 2.
top_k_frequent(items, 3) == [("b", 2), ("a", 2), ("c", 2)]
```

This is the rule the test suite enforces. All three solutions implement it.

## Part 1: Predict Before You Test (20%)

**Do this part before running anything besides `pytest -v tests/test_basic.py`.**
Reading code well is a skill, and the only way to practice it is to commit to
your reading before tools confirm or deny it.

For each of solutions A, B, and C:

1. Read the source file from top to bottom.
2. Write **one paragraph** describing what the function actually does — not what
   the docstring claims it does, but what the code itself does, step by step.

Then make two predictions:

- **Prediction 1:** Which variant breaks first as input size grows? Why?
- **Prediction 2:** Which variant would you trust to run at 3am during an outage?
  "Trust" can mean speed, readability, edge-case handling — name what you mean.

You will be graded on the *quality of your reasoning*, not on whether your
predictions turn out right. A wrong prediction with strong reasoning beats a
right prediction with no reasoning.

```bash
git add WRITEUP.md && git commit -m "Lab 22: Part 1 — predictions"
```

## Part 2: Rank with Evidence (40%)

Rank the three solutions from best to worst. For each variant, write **3–5
sentences citing specific line numbers** that justify its placement.

What "evidence" looks like:

- **Bad:** *"I liked B because it was clean and easy to read."*
- **Good:** *"B sorts every unique item on line 19 even when k is small. For
  inputs with many distinct items, this does work proportional to the number of
  unique items — a heap-based approach would do work proportional to k instead."*

Things to look for:

- **Time complexity** — what does the code do per item, per unique item?
- **Edge cases** — does the code handle k=0, k > len, ties, empty input?
- **Hidden assumptions** — does it mutate the input? Does it stream or buffer?
- **Readability** — could you debug this at 3am?
- **Type discipline** — do the type hints match what the function actually returns?

```bash
git add WRITEUP.md && git commit -m "Lab 22: Part 2 — ranking and evidence"
```

## Part 3: Confirm with Tools (15%)

Now you get to use tools.

### Run the benchmark

```bash
python3 benchmark.py
```

This produces two timing tables. Paste both into your writeup.

The first table holds the vocabulary fixed (50 distinct items) and grows the
input. The second table grows the vocabulary along with the input. The
difference between the two regimes is one of the most important lessons in
this lab — pay attention to it.

### Run mypy

```bash
mypy --strict src/solution_a.py src/solution_b.py src/solution_c.py
```

Paste the output into your writeup.

### Then write one paragraph

- Did the benchmark numbers confirm or change your ranking from Part 2?
- Which variant did `mypy --strict` catch? What did it say?
- Was the Regime 1 picture different from the Regime 2 picture? What does the
  difference suggest about *which kind of workload each variant is suited for*?

```bash
git add WRITEUP.md && git commit -m "Lab 22: Part 3 — benchmark and mypy"
```

## Part 4: Context Shifts the Answer (15%)

The "best" solution depends on the constraint set. This is the part most CS
courses skip, and it is the part working engineers spend the most time on.

Answer both scenarios in 3–5 sentences each. **Take a position and defend it.**
"It depends" without a defended choice loses half the points.

- **Scenario A — small, infrequent.** Input is guaranteed to be under 50 items.
  The function runs once a week in a cron job. Does your ranking from Part 2
  change? Why or why not?
- **Scenario B — hot path.** The function runs 10,000 times per second on the
  request path of a service. The workloads look like Regime 2 from the
  benchmark — many distinct items. Does your ranking change? What additional
  concerns surface that didn't matter in Scenario A?

```bash
git add WRITEUP.md && git commit -m "Lab 22: Part 4 — context shifts"
```

## Part 5: Write the PR Comment (10%)

Pick the variant you would **reject** in a real code review. Write the actual
comment you would leave on the pull request.

A good comment is:

- **Specific** — names the lines and the actual problem
- **Actionable** — suggests a direction for the fix
- **Professional** — talks to a colleague, not a punching bag

The skill being graded is *how do I tell someone their code is wrong without
making them defensive.* It is a skill almost no CS course teaches and almost
every engineering team relies on.

Aim for 4–8 sentences. Longer is not better.

```bash
git add WRITEUP.md && git commit -m "Lab 22: Part 5 — PR comment"
```

## After You Submit

The hidden test suite (`tests/test_hard.py`) covers edge cases the basic suite
does not — empty input, k=0, k larger than the unique count, all-unique input.
After you finish your writeup, run it:

```bash
pytest -v tests/test_hard.py
```

If your ranking from Part 2 *would have changed* knowing about these cases,
that is worth noting in your writeup. It is not a grade penalty — it is the
realization most experienced reviewers eventually have, that they didn't ask
the questions the tests are now asking. Better to notice it now.

## Key Concepts

| Concept | What it means |
|---------|--------------|
| **Code review** | Reading code with the goal of judging its fitness for purpose, not just its correctness |
| **Quality gradient** | Multiple solutions can all be correct yet differ a lot in performance, clarity, or edge-case handling |
| **Complexity-vs-input shape** | Worst-case complexity often depends on input characteristics (vocabulary size, distribution) — fixed-vocabulary inputs hide problems that variable-vocabulary inputs expose |
| **Lying type hints** | A return type that does not match what the function actually returns. `mypy --strict` catches these — the runtime usually does not |
| **Context-dependent quality** | The best solution for a once-a-week cron job is rarely the best solution for a hot path. "Best" requires a "best for what" |
| **Constructive code review** | Telling a colleague their code is wrong in a way that improves the code without damaging the relationship |

## Submission

Push your `WRITEUP.md` and submit your repo URL on Canvas.

Your commit history should look something like:

```
Lab 22: Part 1 — predictions
Lab 22: Part 2 — ranking and evidence
Lab 22: Part 3 — benchmark and mypy
Lab 22: Part 4 — context shifts
Lab 22: Part 5 — PR comment
```

```bash
git push
```
