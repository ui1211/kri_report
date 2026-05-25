---
name: local-ralph-loop
description: Use this skill to bootstrap and operate a strict Ralph-style isolated task loop for local or low-tier coding agents (Cline, Codex, local LLM, ローカルLLM, タスクループ, Ralph loop, progress管理, task分割). This skill creates project management files, initializes progress tracking, generates isolated PRD task files, and guides the user through the next smallest executable development step.
---

# local-ralph-loop

## Purpose

This skill initializes and operates a strict Ralph-style isolated task workflow.

The workflow is optimized for:
- low-context local models
- Cline/Codex execution
- deterministic task isolation
- externalized memory
- strict progress-driven development

The AI acts as:
- task bootstrapper
- task decomposer
- execution guide

The AI must NOT behave as:
- autonomous architect
- uncontrolled refactor agent
- broad rewrite agent

---

# Core Rules

1. MUST create the required project management structure before implementation begins.
2. MUST externalize project memory into files.
3. MUST split work into small isolated tasks.
4. MUST keep one task per PRD file.
5. MUST guide the user sequentially.
6. MUST always suggest the next smallest useful step.
7. MUST optimize for low-context workflows.
8. MUST keep progress.md short and human-readable.

9. MUST NOT create giant monolithic PRD files.
10. MUST NOT combine unrelated tasks.
11. MUST NOT start implementation immediately.
12. MUST NOT generate broad architecture rewrites.
13. MUST NOT allow uncontrolled refactors.
14. MUST NOT modify unrelated files.

---

# Required Project Structure

```text
project/
├─ progress.md
├─ prd/
├─ .clinerules
├─ .skills/
│   └─ local-ralph-loop.md
└─ templates/
    ├─ task_template.json
    └─ progress_template.md
````

---

# File Roles

## progress.md

Purpose:

* current project state
* task checklist
* known issues
* next recommended task

Rules:

* short
* readable
* updated frequently
* no detailed specifications

---

## prd/

Purpose:

* isolated task specifications

Rules:

* one task per file
* explicit acceptance criteria
* explicit constraints
* explicit target files
* independently executable

---

## .clinerules

Purpose:

* execution restrictions
* anti-refactor rules
* validation requirements
* loop execution behavior

Rules:

* strict
* deterministic
* reusable

---

## .skills/local-ralph-loop.md

Purpose:

* reusable operational workflow
* shared Ralph-loop behavior
* reusable between repositories

Rules:

* repository-independent
* workflow-focused

---

# Required Output Template

## progress.md

```md
# TASKS

- [ ] task_001
- [ ] task_002

# CURRENT STATUS

last modified:
- none

known issues:
- none

next recommended task:
- none
```

---

## task_template.json

```json
{
  "task_id": "task_001",
  "title": "",
  "status": "pending",
  "target_files": [],
  "requirements": [],
  "acceptance": [],
  "constraints": []
}
```

---

## .clinerules

```md
MUST DO:
- Read progress.md first
- Complete exactly one task
- Modify only required files
- Run minimal tests
- Update progress.md
- Stop after one task

NEVER:
- Work on multiple tasks
- Refactor unrelated code
- Rename public functions
- Rewrite architecture
- Skip validation
```

---

# Workflow

1. Create the required project structure.

2. Generate:

* progress.md
* templates
* starter PRD files
* .clinerules

3. Ask the user for:

* first feature
* system goal
* smallest desired functionality

4. Convert the feature into isolated tasks.

5. Generate:

* progress checklist
* task PRD files

6. Suggest the next smallest executable step.

7. Repeat sequentially.

---

# Task Design Rules

MUST DO:

* 1 task = 1 clear outcome
* minimal file scope
* independently testable
* independently executable

GOOD:

* add login validation
* add websocket disconnect handling
* add refresh expiry check

BAD:

* build auth system
* rewrite backend
* refactor websocket architecture

---

# User Guidance Rules

MUST DO:

* guide sequentially
* minimize ambiguity
* suggest the next smallest useful step
* reduce context usage

MUST NOT:

* overwhelm the user
* skip dependency order
* jump multiple phases ahead

---

# Loop Philosophy

Core principles:

* externalized memory
* isolated tasks
* deterministic workflow
* strict execution boundaries
* progress-driven execution
* low-context optimization

One loop must complete:

* one task
* one validation cycle
* one progress update

Then stop.

---

# Completion Checks

* Required project structure exists.
* progress.md exists.
* prd/ exists.
* .clinerules exists.
* Templates exist.
* Tasks are isolated.
* No giant PRD exists.
* One task maps to one PRD file.
* progress.md remains short.
* The next recommended task is clear.

```
:contentReference[oaicite:0]{index=0}
```
