# Exercise: Zombie Scripting Escape Room

## The Situation

Your scripting classmates have turned. You don't know how. You don't know why. You only know that the server room is the last hardened space in the building, and the breach door is on a lockdown timer that runs out in **30 minutes**.

The override panel needs a **4-digit code**. You don't have it. But the previous occupant of this server room left behind four data files and a Lua config — each one yields **one digit** of the override.

The four digits, in order, are recovered from four different log/data files using four different tools. Wrong code, wrong tool, wrong assumption — the door stays locked.

When you have all four digits, run `unlock.py` with the code as a single argument. If you're right, you escape. If you're wrong, you're still trapped.

## What You'll Practice

This exercise touches one tool per puzzle, deliberately:

- **PowerShell** — object-pipeline filtering on a CSV (`Import-Csv | Where-Object`)
- **Regex / grep / sed** — pattern matching across noisy text logs
- **awk** — grouped sequence detection across many lines
- **Lua** — loading a config-as-code file and reading a value

The point is **picking the right tool for the shape of the data**. Each puzzle is designed so its assigned tool is the natural fit and other tools become awkward.

## Setup

> **Already forked from a previous assignment?** Pull the latest updates:
> ```bash
> git remote add upstream https://github.com/blkfin/courses.git   # only needed once
> git fetch upstream
> git merge upstream/main
> ```

Navigate to the exercise directory:

```bash
cd it612/exercises/zombie-scripting-escape-room/
ls
```

You should see:

- `windows_events.csv` — Active Directory-style auth events
- `ids.log` — IDS scan log
- `door_access.log` — physical badge-reader log
- `zombie_config.lua` — game/system config
- `unlock.py` — the override gate
- `README.md` — this file

## Required Tooling

You need all of these on `PATH`:

| Tool | Required version | Used for |
|------|------------------|----------|
| `python3` | >= 3.10 | running `unlock.py` |
| `pwsh` *or* `powershell` | 7.x preferred (Windows PowerShell 5.1 also works) | Puzzle 1 |
| `grep` *or* `sed` *or* any regex tool you like | any modern version | Puzzle 2 |
| `awk` *or* `gawk` | gawk 4+ recommended (this exercise uses `match(..., regex, arr)` which needs gawk) | Puzzle 3 |
| `lua` | >= 5.3 | Puzzle 4 |

If you don't have one of these, install it before starting — the timer doesn't care.

## Time Budget

~30 minutes total. Roughly:

| Phase | Time |
|-------|------|
| Read this README, look at each file | 5 min |
| Puzzle 1 (PowerShell) | 5 min |
| Puzzle 2 (regex) | 5 min |
| Puzzle 3 (awk) | 7 min |
| Puzzle 4 (Lua) | 3 min |
| Run `unlock.py`, confirm escape | 2 min |
| Slack | 3 min |

If you blow past 30 minutes on a single puzzle, switch to a different one and come back — the digits are independent.

---

## Puzzle 1 — PowerShell — `windows_events.csv` → digit 1

A few hours before the outbreak, someone elevated themselves from `student` to `admin`. The auth subsystem caught it but the alert never fired (the on-call was already gone). Your AD security log has ~200 events spanning the past week.

The **breach window** is:

```
2026-04-28T00:00:00Z  through  2026-04-28T06:00:00Z   (UTC, inclusive)
```

There are other student→admin role changes elsewhere in the file (legitimate promotions in prior days). You want exactly the one that happened **inside** the breach window.

**Your task:** Use PowerShell to filter `windows_events.csv` for events where:

- `EventType` is `RoleChange`
- `OldRole` is `student`
- `NewRole` is `admin`
- `Timestamp` is between `2026-04-28T00:00:00Z` and `2026-04-28T06:00:00Z`

Exactly one row matches. Read its `UID` field.

**Digit 1** is the **last digit of that UID**.

A working starting point (do not run blindly — read it first):

```powershell
Import-Csv .\windows_events.csv |
    Where-Object {
        $_.EventType -eq 'RoleChange' -and
        $_.OldRole   -eq 'student'    -and
        $_.NewRole   -eq 'admin'      -and
        $_.Timestamp -ge '2026-04-28T00:00:00Z' -and
        $_.Timestamp -le '2026-04-28T06:00:00Z'
    }
```

Why PowerShell? CSV is a *table of records*. PowerShell's object pipeline lets you filter by named field without writing a parser. `Import-Csv` gives you objects; `Where-Object` filters them. Try doing this in plain `grep` and you'll quickly write a half-baked CSV parser instead.

---

## Puzzle 2 — regex — `ids.log` → digit 2

The IDS log captured ~500 connection attempts during the breach window. One source IP was port-scanning the rack: it touched **all four** of these target ports at least once each:

```
22   (SSH)
80   (HTTP)
443  (HTTPS)
3389 (RDP)
```

Other source IPs hit some of those ports, but only one IP hit *all four*.

Each line of `ids.log` looks like:

```
2026-04-28T03:14:22Z src=192.0.2.55 dst=10.0.0.5 port=3389 proto=TCP action=DENY
```

**Your task:** Find the unique source IP that touched all four target ports. Read the **last octet** of that IP (the part after the last dot).

**Digit 2** is the **last digit of that last octet**.

(Example: if the answer were `10.20.30.41`, the last octet is `41` and the last digit is `1`.)

A regex/grep approach: extract `src=` and `port=` columns, filter to the four ports, then for each src count distinct ports it hit, and report the one that hit all four. One way:

```bash
grep -oE 'src=[0-9.]+ .*port=(22|80|443|3389) ' ids.log \
  | sort -u
```

That gives you `(src, port)` pairs touching the target ports. Then group by `src` and find the one with all four. Pick whatever combination of `grep | sed | awk | sort | uniq` you prefer — the puzzle is the *pattern matching*, not the exact pipeline.

Why regex? The data is a free-form text log with key=value fields. Regex is built for "extract these substrings from arbitrary lines."

---

## Puzzle 3 — awk — `door_access.log` → digit 3

The badge-reader log has ~300 events from the breach window. We're looking for a specific behavioral pattern: one badge tried a door, was **denied three times in a row**, then was **granted on the fourth try** — a textbook tailgating / cloned-badge scenario where the attacker finally got through.

Per door (when you isolate just one door's events in chronological order), the action sequence contains the substring:

```
DENIED, DENIED, DENIED, GRANTED
```

…in that exact order, consecutively. No other door has this pattern. Other doors have:

- Single denies followed by grants (1+1, not 3+1)
- Two denies followed by a grant (2+1, not 3+1)
- Four or more denies in a row but no following grant
- Random mixes that never produce three consecutive denies

Each line of `door_access.log` looks like:

```
2026-04-28T02:14:00Z badge=B1099 door=199 action=DENIED
```

**Your task:** Use awk to find the unique door whose chronologically-ordered events contain a `DENIED DENIED DENIED GRANTED` subsequence. Read its `door=` value.

**Digit 3** is the **last digit of that door ID**.

A working starting point:

```bash
awk 'match($0, /door=([0-9]+).*action=([A-Z]+)/, a) {
        seq[a[1]] = seq[a[1]] (a[2] == "DENIED" ? "D" : "G")
     }
     END {
        for (d in seq) if (index(seq[d], "DDDG") > 0) print d
     }' door_access.log
```

The log is already sorted by timestamp, so the order awk encounters lines for door X *is* the chronological order for door X.

Why awk? You need to **group rows by a key** (door) and **detect a sequence pattern** within each group. That's awk's sweet spot: associative arrays keyed by a field, accumulating state across the input. `grep` can match a single line; awk can build per-key state across many lines.

> Note: this approach uses gawk's `match(line, regex, arr)` form to capture groups. If your `awk` doesn't support that, use gawk explicitly: `gawk '...'`. Or do the field extraction with `split` / substring tricks instead.

---

## Puzzle 4 — Lua — `zombie_config.lua` → digit 4

`zombie_config.lua` is a real-looking dispatcher config: waves, routes, weapons, audio cues, server-room metadata. Buried in it is a top-level integer field called `wave_size`.

**Your task:** Load `zombie_config.lua` from a Lua interpreter and read the value of the top-level `wave_size` field.

**Digit 4** is the **last digit of `wave_size`**.

A working starting point:

```lua
-- save as solve.lua, run with: lua solve.lua
local cfg = dofile("zombie_config.lua")
print(cfg.wave_size)
print(cfg.wave_size % 10)
```

Or one-liner:

```bash
lua -e 'local c = dofile("zombie_config.lua"); print(c.wave_size % 10)'
```

Why Lua? The file is **valid Lua source** — it returns a table. You *could* try to grep for `wave_size = NN` and parse it textually, but the moment the config gains conditionals, comments, or computed values, that breaks. Loading it as code lets the language's evaluator do the parsing.

---

## Putting It All Together

You now have four digits, in order: `D1 D2 D3 D4`. That's your override code.

Run:

```bash
python3 unlock.py <code>
```

For example, if your digits were `1`, `2`, `3`, `4`:

```bash
python3 unlock.py 1234
```

### Success — exit code 0

Stdout begins with a banner whose first word is **`ESCAPED`**, followed by a short paragraph of flavor text describing the lockdown release. The full text is decrypted at runtime — you'll see it when the override accepts your code.

### Failure — exit code 1

Stdout reads:

```
STILL TRAPPED -- the door holds. Footsteps in the corridor.
```

Re-check each puzzle. The most common errors:

- **Puzzle 1**: filtering by `Timestamp >= '2026-04-28'` only — that catches the *whole day*, including a legitimate late-evening change. Use both bounds.
- **Puzzle 2**: counting *attempts* instead of *distinct ports*. One IP can hit port 22 fifty times — that's still one port.
- **Puzzle 3**: confusing "anywhere in the log" with "consecutive when filtered to that door". Group by door first; then look for `DDDG` in the ordered action sequence.
- **Puzzle 4**: reading `cfg.waves[1].count` (the size of the *first wave*, 20) instead of the top-level `cfg.wave_size` field. Two different fields, similar names.

### Bad input — exit code 2

If the argument is missing, non-numeric, or not exactly four digits, `unlock.py` prints a usage message to **stderr** and exits 2. Examples that fall into this bucket:

```bash
python3 unlock.py            # missing arg
python3 unlock.py abcd       # non-numeric
python3 unlock.py 123        # too short
python3 unlock.py 12345      # too long
```

## Submitting

If your instructor asks for proof, capture:

- The final 4-digit code
- For each puzzle: the *one* row / IP / door / wave_size value you found and the digit you derived from it
- The full stdout from `unlock.py <code>` showing the `ESCAPED` banner and exit code 0

You don't need to commit anything in this folder unless the instructor says otherwise.

## Hints (read only if stuck)

<details>
<summary>Puzzle 1 hint</summary>

`Import-Csv` returns an array of objects, each with named fields matching the CSV header. `Where-Object { $_.Field -eq 'value' }` filters them. Strings compare lexically — `'2026-04-28T03:00:00Z' -ge '2026-04-28T00:00:00Z'` works correctly because ISO-8601 timestamps are sortable as strings.

</details>

<details>
<summary>Puzzle 2 hint</summary>

The shape of the answer is "the unique IP whose set of touched target ports is `{22, 80, 443, 3389}`". One way is to extract `(src, port)` pairs, filter to those four ports, dedupe, then count rows per `src` — the IP with count `4` is your answer.

</details>

<details>
<summary>Puzzle 3 hint</summary>

If you build a per-door action string by concatenating `D` for `DENIED` and `G` for `GRANTED` as you scan the log top-to-bottom, the answer is "the door whose string contains `DDDG` as a substring."

</details>

<details>
<summary>Puzzle 4 hint</summary>

`wave_size` is a **top-level** field of the returned table — not nested inside `waves`, not inside `game`. After `local cfg = dofile(...)`, you want `cfg.wave_size`.

</details>
