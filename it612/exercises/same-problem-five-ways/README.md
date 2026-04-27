# Exercise: The Same Problem, Five Ways

## Overview

It's the end of the semester. A colleague hands you a folder called `course_export/` and says: *"This is everything from CS 1234. Can you tell me which students submitted Lab 1, which files look suspicious, and which uploads failed?"*

The folder is a mess. Filenames are inconsistent. CSVs duplicate each other (or do they?). Attendance is in plain text. The upload log mixes structured and unstructured lines. Names appear in three different formats.

You're not going to write five complete solutions. You're going to **defend a scripting strategy** based on the shape of the problem.

## What You'll Practice

- Reading messy real-world data and naming what's actually hard about it
- Choosing between text pipelines, object pipelines, regex, and structured scripts
- Anticipating failure modes before writing code
- Communicating a script's contract: inputs, outputs, side effects, dry-run behavior

## Setup

Navigate to the exercise directory:

```bash
cd it612/exercises/same-problem-five-ways/
```

Take a look around:

```bash
ls course_export/
ls course_export/submissions/
cat course_export/logs/upload.log
```

You should see:

- `Grades Final.csv` and `grades-final-2.csv` — two grade files. Which is canonical? Are they the same? Are they both wrong?
- `attendance_04-12.txt` and `attendance 04-19.txt` — attendance from two weeks. Note the formatting drift between them.
- `submissions/` — three Lab 1 submissions with inconsistent filenames.
- `logs/upload.log` — the upload server's log. Mostly structured, occasionally not.

---

## Your Task

In groups, produce a **short plan** for a script or pipeline that answers:

1. **Who submitted Lab 1?** Which students appear in `submissions/`, accounting for the filename inconsistency?
2. **Which files look duplicated, stale, or suspicious?** Are the two grade CSVs the same data? Are there overwrite warnings in the log?
3. **Which upload log lines indicate failures?** Successes? Anomalies?
4. **What report should the instructor see at the end?** What columns? What format?
5. **What toolchain would you use, and why?**

You don't need to fully implement everything. You need a plan you can defend.

---

## Group Lenses

Your group will be assigned **one lens**. Argue the problem from that perspective.

- **Bash pipeline group.** How far can `find`, `grep`, `sed`, `awk`, `sort`, and `uniq` get you? Where does it start to break down?
- **PowerShell group.** What changes if file metadata and CSV rows are treated as objects instead of strings? Where does the object model help, and where is it overkill?
- **Regex group.** Which pieces of this problem are pattern-extraction problems regex handles cleanly? Where does regex become the wrong tool?
- **JS or Lua script group.** When does a small, real script become clearer than a shell pipeline? What's the threshold?
- **Skeptic group.** Your job is to attack every other group's proposed solution. Look for: spaces in filenames, malformed input, duplicated data, portability across OSes, destructive defaults, maintainability for the next person to read it.

---

## Group Deliverable

Each group produces a tiny design note. Use this template:

```markdown
## Group: [bash | powershell | regex | js-lua | skeptic]

**Toolchain:** (one or two tools)

**Why this fits the data:** (what shape of data does your toolchain handle well?)

**First three commands or script steps:**
1.
2.
3.

**What could break:** (filename edge cases, malformed input, locale, etc.)

**What `--dry-run` would show:** (or: should this even have a dry-run?)

**Upgrade path:** (when would we rewrite this as a more structured tool?)
```

Drop this in a file called `group-NN.md` (where NN is your group number) in this directory.

---

## Timing

| Phase                  | Time      |
|------------------------|-----------|
| Group planning         | 5 min     |
| Report-out (each group)| 6–8 min   |
| Instructor debrief     | 4–5 min   |

Total: ~15–18 min.

---

## Wrap-Up

The point of this activity is **not** to find the one correct script. The point is:

- Different data shapes want different tools.
- Real data has edges that punish assumptions.
- Tool selection is a design choice, not a personal preference.

Be ready to argue your group's choice — and to hear another group argue against it.

**Submit:**

```bash
git add -A
git commit -m "Exercise: Same Problem Five Ways — group NN"
git push
```
