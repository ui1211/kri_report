# Workflow Design Guide

This README is a guide for creating and maintaining workflows in this project.

Use it by giving an AI agent:

1. the workflow goal,
2. the expected inputs and outputs,
3. the skills the workflow should call,
4. this README.

The agent should then produce a workflow that is easy for smaller models, such as `qwen3.5:9b`, to execute reliably.

## Workflow vs Skill

Use a skill for a reusable capability.

Use a workflow for orchestration:

- selecting task mode,
- deciding which skill to call,
- sequencing research, formatting, validation, and output,
- defining completion checks across multiple files.

A workflow should not duplicate the full body of each skill. It should reference the skill and state only the orchestration rules.

## Design Principles

- Use English for control instructions.
- Keep final output filenames, headings, labels, and templates in Japanese when the final output is Japanese.
- Prefer deterministic steps over broad guidance.
- Use safe defaults instead of asking unnecessary questions.
- Make task-mode branching explicit.
- State when external research is allowed or forbidden.
- State exact completion checks.
- Keep changelog rules lightweight.

## Recommended Workflow Shape

Use this structure for new workflow files.

````md
# {workflow-name} Workflow

Short purpose statement.

## Required Skills

- `skill-a`: why it is used
- `skill-b`: why it is used

## Task Mode

- Mode A: ...
- Mode B: ...
- Mode C: ...

Default:
- If ..., use ...

## Input Types

- ...

## Workflow

1. Determine task mode.
2. Collect input.
3. Call the required skills in order.
4. Validate output.
5. Finish only when completion checks pass.

## Output Requirements

```md
# 日本語固定テンプレート

## 固定見出し
```

## Completion Checks

- Required files exist.
- Required headings are unchanged.
- No forbidden content remains.

## Do Not

- Do not ...
````

## Language Policy

For workflows targeting small/local models:

- Control instructions: English
- Fixed output templates: Japanese, if the final output is Japanese
- Final generated content: Japanese, if the task is Japanese
- Skill names and filenames: exact literal strings

Useful phrases:

```md
The final output must be written in Japanese.
Do not translate Japanese headings or fixed labels.
Use this mode when ...
Do not perform external search for format-only tasks.
Finish only when all completion checks pass.
```

## Task Mode Rules

Every workflow should define how to choose the task mode without stopping unnecessarily.

Good:

```md
If the user provides an existing document, use update mode.
If the user provides only a topic, use new report mode.
If the user says "format only" or "検索不要", do not perform external search.
```

Avoid:

```md
Always ask the user before starting.
```

## Changelog Policy

Use Git as the source of truth for exact diffs.

Update `plan/CHANGELOG.md` when a workflow or skill change affects:

- triggering behavior,
- output structure,
- required workflow sequence,
- validation rules,
- compatibility with smaller models.

Do not update `plan/CHANGELOG.md` for ordinary generated report content.
Do not duplicate exact diffs in the changelog.
Write why the workflow changed, not every line that changed.

## Validation Checklist

Before accepting a workflow:

- The workflow has a clear purpose.
- Required skills are listed.
- Task modes are explicit.
- Defaults are defined.
- External-search rules are explicit.
- Output filenames and required structures are explicit.
- Completion checks are testable.
- The workflow does not contradict the referenced skills.
- The workflow does not require unnecessary user confirmation.

## AI Prompt Template

Use this prompt when asking an AI agent to create or revise a workflow.

```md
Create or update a workflow for this repository.

Goal:
- {what the workflow should orchestrate}

Expected input:
- {topics, files, notes, URLs, reports, etc.}

Expected output:
- {files, format, language, validation requirements}

Required skills:
- {skill names and responsibilities}

Task modes:
- {new/update/format-only/etc.}

Constraints:
- Use English control instructions.
- Keep Japanese output templates, headings, labels, and filenames unchanged.
- Optimize for small/local models such as qwen3.5:9b.
- Avoid unnecessary user confirmation.
- Include completion checks.

Follow workflows/README.md.
Return the complete workflow Markdown.
```

## Common Failure Modes

- The workflow duplicates skill instructions instead of orchestrating skills.
- The workflow says to use reference IDs while the formatting skill forbids them.
- The workflow always asks the user instead of using safe defaults.
- The workflow does not define format-only behavior.
- The workflow does not define completion checks.
- The workflow updates changelog for ordinary generated content.
