# Skill Design Guide

This README is a guide for creating or updating skills in this project.

Use it by giving an AI agent:

1. the goal of the skill,
2. the expected input and output,
3. examples of user requests,
4. this README.

The agent should then produce a high-quality `SKILL.md` that is easy for smaller models, such as `qwen3.5:9b`, to follow.

## Design Principles

- Keep the skill focused on one job.
- Put triggering information in `description`.
- Use English for control instructions when stability matters.
- Keep required output templates, headings, labels, and final report language in Japanese when the output is Japanese.
- Prefer short imperative rules: `MUST`, `MUST NOT`, `Do not`, `Workflow`, `Completion Checks`.
- Avoid long explanations that do not change agent behavior.
- Do not require unnecessary user confirmation. Make safe default assumptions.
- Do not invent facts, links, numbers, dates, or effects.
- Validate structure before considering the skill complete.

## Recommended SKILL.md Shape

Every skill must have YAML frontmatter with only `name` and `description`.

````md
---
name: skill-name
description: Use this skill when ... Include English trigger terms and Japanese trigger words if users will ask in Japanese.
---

# skill-name

## Purpose

State what the skill does in 1-3 short paragraphs.

State the final output language if relevant.

## Core Rules

1. MUST ...
2. MUST NOT ...
3. Do not ...

## Required Output Template

Keep fixed user-facing headings and labels exactly as required.

```md
# 日本語タイトル

## 固定見出し
- 固定ラベル:
```

## Workflow

1. Read or extract ...
2. Transform ...
3. Validate ...
4. Output ...

## Completion Checks

- Required structure exists.
- Required labels are unchanged.
- No forbidden content is present.
- The output matches the user's requested language and format.

## Do Not

- Do not ...
- Do not ...
````

## Description Rules

The `description` field is the main trigger surface. Write it so an agent can decide when to load the skill without reading the body.

Good description:

```yaml
description: Use this skill to create or update Japanese research reports (調査レポート, レポート作成). It formats notes into a fixed Japanese Markdown structure with inline links, issue IDs, and validation checks.
```

Avoid vague descriptions:

```yaml
description: レポートを作るスキル
```

Use quoted YAML strings when the description contains a colon:

```yaml
description: "Use this skill for fixed output sections: 要約, 現状, 課題, 解決, 価値."
```

## Language Policy

For small or local models, use this split:

- Control instructions: English
- Fixed output templates: Japanese, if the final output is Japanese
- User-facing final output: Japanese, if the task is Japanese
- Keywords in `description`: English plus important Japanese trigger words

Example:

```md
The final output must be written in Japanese.
Do not translate the required Japanese headings.
Keep this template exactly.
```

## Output Template Rules

When a skill requires a fixed output format:

- Put the complete template in `Required Output Template`.
- Say clearly that headings and labels must not be translated.
- Include placeholders only where the agent may write content.
- Include a completion checklist that checks the same structure.
- Do not describe multiple competing templates in the same skill unless the workflow clearly selects one.

## Validation Checklist

Before accepting a new or updated skill:

- `SKILL.md` exists in `skills/{skill-name}/`.
- Frontmatter has valid YAML.
- Frontmatter contains `name` and `description`.
- `name` matches the folder name.
- `description` explains when to use the skill.
- The body has `Purpose`, `Core Rules` or equivalent, `Workflow`, and `Completion Checks`.
- Required templates are explicit.
- Prohibited behavior is explicit.
- The skill does not depend on hidden context.
- The skill does not ask the user questions that can be resolved with safe defaults.

Run validation:

```powershell
$env:PYTHONUTF8='1'
python C:\Users\yutou\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills\{skill-name}
```

## AI Prompt Template

Use this prompt when asking an AI agent to create or revise a skill.

```md
Create or update a Codex skill.

Goal:
- {what the skill should do}

Expected users:
- {who will use it}

Expected input:
- {topics, files, notes, code, URLs, etc.}

Expected output:
- {format, language, files, templates}

Important constraints:
- {must keep}
- {must not do}
- {validation requirements}

Model target:
- Optimize for small/local models such as qwen3.5:9b.
- Use English control instructions.
- Keep final output templates in Japanese when the output is Japanese.

Follow this repository's skills/README.md.
Return the complete SKILL.md.
```

## Common Failure Modes

- The skill has a vague `description`, so it does not trigger reliably.
- The skill mixes instructions and output content in a way that changes the final template.
- The skill says both "use inline links only" and "add reference IDs".
- The skill requires user confirmation before every run.
- The skill tells the model to be flexible when the output must be fixed.
- The skill allows unsupported inference instead of requiring `不明`.
- The skill has no completion checklist.

## Report Skill Convention

For report-related skills in this project:

- Main report format: `report-format-kri`
- A4 summary format: `report-format-a4`
- Fact checking: `report-fact-check`
- End-to-end workflow: `research-report`

Do not create a new report formatting skill unless it has a clearly different output contract.
