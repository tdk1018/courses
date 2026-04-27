# Lab 20: Build the Other Side

## Bridge from Lab 19

In Lab 19, you were the client — calling CoinGecko, handling status codes, building a cache. Someone else built that server. Someone else decided what happens when you send a bad request, or when you ask too fast, or when the data isn't ready yet.

This lab puts you on the other side. You'll build a server using FastAPI, write a client that talks to it, and discover — by breaking things — why APIs need to be designed carefully.

**Starter files:**
```
Lab20/
├── conftest.py            # Test config (already done)
├── requirements.txt       # Dependencies (already done)
├── server.py              # You build this
├── client.py              # You build this
├── grading.py             # Provided — fake grading engine
└── tests/
    ├── test_naive.py
    ├── test_retry.py
    ├── test_idempotent.py
    ├── test_async.py
    └── test_smart_client.py  # Bonus
```

**Test command:** `python -m pytest tests/ -v`

## Setup

This lab uses **FastAPI** — a Python framework for building APIs. In your Codespace terminal:

```bash
cd Lab20
pip install -r requirements.txt
```

To run your server manually (useful for testing with your client):
```bash
uvicorn server:app --reload
```

This starts your server at `http://localhost:8000`. The `--reload` flag restarts the server whenever you save a file. You'll want two terminals open: one running the server, one for running your client code or tests. (In Codespaces, click the **+** button in the terminal panel to open a second terminal.)

## Background: What's a Server, Really?

In Lab 19, you used `requests.get()` to ask CoinGecko for data. Something on the other end received your request, figured out the answer, and sent it back.

That "something" is a **server** — a program that listens for incoming requests and returns responses. FastAPI lets you build one in Python.

Here's the simplest possible FastAPI server:

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/echo")
def echo(data: dict):
    return {"you_sent": data}
```

The `@app.post("/echo")` line is a **decorator** — it tells FastAPI "when someone sends a POST request to `/echo`, run this function." The function receives the JSON request body as `data` and returns a dictionary, which FastAPI automatically converts to JSON.

On the client side, you already know how to call this:

```python
import requests

response = requests.post("http://localhost:8000/echo", json={"hello": "world"})
print(response.json())  # {"you_sent": {"hello": "world"}}
```

Same `requests` library from Lab 19. Same JSON. Now you control both sides.

## The Running Example

You're building a **grading API**. A student submits their work, the server grades it, and the client gets the score back.

The grading logic is already written for you. Open `grading.py` and read it before you start — it's short. The `grade()` function takes a student name and lab number and returns a deterministic score (it's based on a hash, not real grading). It also has a `slow` parameter that makes grading take a few seconds. You'll need that later.

---

## Task 1: The Naive Server

Open `server.py`. Build a FastAPI app with one endpoint:

**`POST /grade`**

It should:
1. Accept a JSON body with `"student"` (a string) and `"lab"` (an integer)
2. Call `grade(student, lab)` from `grading.py` to get the score
3. Return a JSON response: `{"student": student, "lab": lab, "score": score}`

Then open `client.py` and write:

**`submit(student, lab, base_url="http://localhost:8000")`**

It should:
1. Send a POST request to `{base_url}/grade` with the student and lab as JSON
2. Check that the status code is `200` — raise a `RuntimeError` if it isn't
3. Return the response as a dictionary (use `.json()` like you did in Lab 19)

Run the tests:
```bash
python -m pytest tests/test_naive.py -v
git add -A && git commit -m "Lab 20: Implement naive server and client"
```

Want to see it work for real? Open two terminals. In the first one, start the server:
```bash
uvicorn server:app --reload
```

In the second, open a Python shell:
```python
from client import submit
print(submit("alice", 19))
```

This works. The server grades, the client gets the score, everyone's happy. Let's break it.

---

## Task 2: Retries Reveal a Problem

### The Setup

What happens when grading is slow? Your server can already handle this — the `grade()` function accepts a `slow` parameter. When `slow=True`, grading takes about 3 seconds instead of being instant.

**Update your `POST /grade` endpoint** to check for an optional `"slow"` field in the request body. You can use `data.get("slow", False)` — the `.get()` method returns the value if the key exists, or the default (`False`) if it doesn't. Pass the result to `grade()`. This way Task 1's behavior doesn't change, but the client can now request slow grading.

A real client won't wait forever. If you set a 2-second timeout and grading takes 3 seconds, the client gives up. Retrying is the standard response — you saw this instinct in Lab 19 when API calls looked stuck.

But here's the thing: a timeout means **the client stopped waiting**. It doesn't mean the server stopped working.

### What to Build

**Update `server.py`:**

Add a list called `grading_log` at the top of your file (outside any function — this makes it shared across all requests). Every time the server grades a submission, append a record to this log:
```python
{"student": student, "lab": lab, "score": score}
```

Also add two utility endpoints:

- **`GET /log`** — returns `{"entries": grading_log}`
- **`POST /reset-log`** — clears the log and returns `{"status": "cleared"}`

The log lets you (and the tests) see exactly how many times the server actually did work.

**Update `client.py`:**

Write a new function:

**`submit_with_retry(student, lab, base_url="http://localhost:8000", timeout=2, max_retries=3)`**

It should:
1. POST to `/grade` with `{"student": student, "lab": lab, "slow": True}`
2. Pass the `timeout` parameter to `requests.post()` (e.g., `requests.post(url, json=data, timeout=timeout)`)
3. If the request raises `requests.exceptions.Timeout`, catch it and try again
4. Retry up to `max_retries` times total
5. If all retries time out, raise `RuntimeError("all retries failed")`
6. If any attempt succeeds, return the response dictionary

### The Discovery

Run the tests:
```bash
python -m pytest tests/test_retry.py -v
```

One of these tests calls `POST /grade` three times and then checks the server log. Think about this before you look at the test output: **if the client retried 3 times, how many entries are in the server's grading log?**

Three. Every retry triggers a new grading run on the server. The server doesn't know about the client's impatience — each request looks identical. If this were a real system (billing, enrollment, grading that counts), you'd have duplicate side effects.

```bash
git add -A && git commit -m "Lab 20: Add retry logic and grading log"
```

---

## Task 3: Idempotency Makes Retries Safe

The fix is conceptually simple: **give each submission a name**. If the server has already seen that name, skip the work and return the previous result.

This property — doing something twice has the same effect as doing it once — is called **idempotency**. The name comes from math: an idempotent operation is one where `f(f(x)) = f(x)`.

### What to Build

**Update `server.py`:**

Add a dictionary called `completed` at the top of your file (same level as `grading_log`). This maps submission IDs to their results.

Update your `POST /grade` endpoint to:
1. Check for an optional `"submission_id"` field in the request body
2. If `submission_id` is provided AND exists in `completed`, return the cached result — **don't call `grade()` again, don't add to the log**
3. If `submission_id` is new (or not provided), grade normally. If `submission_id` was provided, store the result in `completed` keyed by that ID
4. Requests without `submission_id` should work exactly like before (no caching)

Also add a utility endpoint:

- **`POST /reset-completed`** — clears the `completed` cache and returns `{"status": "cleared"}`

**Update `client.py`:**

Write a new function:

**`submit_idempotent(student, lab, base_url="http://localhost:8000", timeout=2, max_retries=3)`**

Same retry logic as `submit_with_retry`, but with one addition:
1. Generate a stable submission ID: `f"{student}-lab{lab}"`
2. Include it in the JSON body as `"submission_id"`

The key word is **stable** — the same student and lab always produce the same ID. That's what makes retries safe: the server recognizes the repeated intent.

### Think About This

What would happen if the client used a random ID for each retry instead of a stable one? The server would see each retry as a brand new submission. The idempotency key only works because it names the **intent** ("grade Alice's Lab 19"), not the **request** ("this particular HTTP call").

```bash
python -m pytest tests/test_idempotent.py -v
git add -A && git commit -m "Lab 20: Add idempotency"
```

---

## Task 4: Honest About Time

Idempotency solved the duplication problem, but the client still has a frustrating experience. It sends a request, waits 2 seconds, gets nothing, retries — even though the server is working just fine. The API is **lying by omission**: a hanging connection tells the client nothing about what's happening on the other side.

A better design: the server immediately says "got it, I'm working on it" and lets the client check back later.

### New Status Code: 202 Accepted

You've seen `200 OK` — it means "here's your answer." There's another code that means something different:

**`202 Accepted`** — "I received your request and I'm working on it, but the result isn't ready yet."

The difference matters. `200` after 30 seconds of silence feels the same as a timeout. `202` immediately tells the client: I heard you, check back later.

### What to Build

**Update `server.py`:**

You'll need two new imports at the top:
```python
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
```

Add two more dictionaries at the top of your file:
- `jobs` — maps job IDs to their status (e.g., `{"status": "pending"}` or `{"status": "complete", "result": {...}}`)
- `job_submission_map` — maps submission IDs to job IDs (for idempotency)

You'll also need a way to generate unique job IDs. You can use Python's `uuid` module:
```python
import uuid
job_id = str(uuid.uuid4())  # e.g., "a8098c1a-f86e-11da-bd1a-00112444be1e"
```

Add a new endpoint:

**`POST /grade-async`**

1. Accept a JSON body with `"student"`, `"lab"`, and optionally `"submission_id"`
2. **Idempotency check**: if `submission_id` is provided and already maps to a job, return that job's current status (don't create a new job)
3. Otherwise: generate a new job ID, store `{"status": "pending"}` in `jobs`, and kick off grading in the background
4. Return **immediately** with status code `202`:
   ```python
   return JSONResponse({"job_id": job_id, "status": "accepted"}, status_code=202)
   ```

For the background work, use FastAPI's `BackgroundTasks`. Add it as a parameter to your endpoint function — FastAPI will automatically provide it for you (the same way it provides `data`):

```python
@app.post("/grade-async")
def grade_async(data: dict, background_tasks: BackgroundTasks):
    # ... create job, check idempotency ...
    background_tasks.add_task(run_grade_job, job_id, student, lab)
    return JSONResponse({"job_id": job_id, "status": "accepted"}, status_code=202)
```

`add_task` tells FastAPI: "after you send the response, call this function with these arguments." The endpoint returns immediately — the grading happens afterward.

Write a helper function `run_grade_job(job_id, student, lab)` that:
1. Calls `grade(student, lab, slow=True)` (the slow version — that's the whole reason we need async)
2. Builds the result dictionary: `{"student": student, "lab": lab, "score": score}`
3. Adds an entry to `grading_log`
4. Updates the job: `jobs[job_id] = {"status": "complete", "result": result}`

Add a status-checking endpoint:

**`GET /grade-jobs/{job_id}`**

1. If the job ID doesn't exist, return status code `404`: `JSONResponse({"error": "job not found"}, status_code=404)`
2. If the job is pending: `{"job_id": job_id, "status": "pending"}`
3. If the job is complete: `{"job_id": job_id, "status": "complete", "result": {...}}`

**Update `client.py`:**

Write a new function:

**`submit_async(student, lab, base_url="http://localhost:8000", poll_interval=0.5, max_polls=20)`**

1. Generate a stable `submission_id` (same pattern as Task 3)
2. POST to `/grade-async` with `student`, `lab`, and `submission_id`
3. Expect a `202` response — raise `RuntimeError` if you get something else
4. Extract the `job_id` from the response
5. **Poll**: in a loop, send GET requests to `/grade-jobs/{job_id}` every `poll_interval` seconds (use `time.sleep(poll_interval)` between requests)
6. When the status is `"complete"`, return the `result` dictionary
7. If you hit `max_polls` without getting a `"complete"`, raise `RuntimeError("polling timed out")`

### What Changed

Notice: no timeouts, no retries. The client gets an immediate answer ("accepted"), then checks back at its own pace. There's no ambiguity about whether the server received the request. The API is **honest about time**.

```bash
python -m pytest tests/test_async.py -v
git add -A && git commit -m "Lab 20: Add async grading with polling"
```

---

## Bonus Task 5: The Smart Client

Build a `SmartClient` class in `client.py` that handles everything:

```python
client = SmartClient(base_url="http://localhost:8000")
result = client.submit("alice", 19)
```

Under the hood, it should:
1. Generate a stable `submission_id`
2. Try the sync endpoint first (`POST /grade`) with a timeout
3. If it gets a `200`, return the result
4. If it times out, fall back to the async endpoint (`POST /grade-async`)
5. Poll until complete
6. Return the same result format either way

One interface that adapts to whether the server is fast or slow, with idempotency built in so retries are always safe.

```bash
python -m pytest tests/test_smart_client.py -v
git add -A && git commit -m "Lab 20: Bonus — SmartClient"
```

---

## Writeup Questions

Answer these in a file called `WRITEUP.md` in your Lab20 directory. A few sentences each is fine.

1. **The timeout trap.** When the client times out, does that mean the server failed? What's actually happening on the server side when the client gives up waiting?

2. **Naming your intent.** What would happen if the idempotency key were a random UUID generated fresh on each retry, instead of a stable `f"{student}-lab{lab}"`? Would retries still prevent duplicate grading? Why or why not?

3. **Sync vs. async.** The CoinGecko API from Lab 19 returned prices immediately (sync). The grading API in Task 4 returns a job ID and makes you poll (async). What's the deciding factor for when an API should use each approach?

4. **Hidden state.** The lecture says "the API hides state from you." Where in this lab did you experience hidden state? What was hidden, and what design decision made it visible?

---

## Key Concepts

| Concept | What It Means |
|---------|--------------|
| Server | A program that listens for requests and returns responses |
| FastAPI | A Python framework for building HTTP APIs |
| Endpoint | A URL path + HTTP method that the server responds to (e.g., `POST /grade`) |
| Decorator | The `@app.post(...)` syntax that registers a function as an endpoint |
| Status code 200 | OK — the request succeeded and the result is ready |
| Status code 202 | Accepted — the server received the request but is still working on it |
| Status code 404 | Not Found — the requested resource doesn't exist |
| Timeout | The client stopped waiting — not necessarily a server failure |
| Retry | Sending the same request again after a failure or timeout |
| Idempotency | The property that doing something twice has the same effect as doing it once |
| Idempotency key | A stable identifier that lets the server recognize repeated requests |
| Polling | Repeatedly checking a status endpoint until work is complete |
| BackgroundTasks | FastAPI's mechanism for running work after sending a response |

## Submission

Push your work to your repository. Your commit history should show your progression:

```
Lab 20: Implement naive server and client
Lab 20: Add retry logic and grading log
Lab 20: Add idempotency
Lab 20: Add async grading with polling
Lab 20: Bonus — SmartClient          (if attempted)
Lab 20: Add writeup
```
