---
name: report-format-a4
description: "Use this skill to create a Japanese A4-style summary (A4要約) from an existing report or notes. The output must be Japanese, must not add new information, and must keep the fixed 5-section structure: 要約, 現状, 課題, 解決, 価値."
---

# report-format-a4

## Purpose

Compress existing information into a short Japanese A4-style summary.

This skill is for summarization only. Do not perform new research. Do not add explanations, facts, numbers, or claims that are not in the input. If a main report exists, use only that report as the source.

The final output must be written in Japanese. Do not translate the required Japanese headings.

## Core Rules

1. MUST keep exactly the five required sections.
2. MUST NOT add information that is not in the input.
3. Use `不明`, `記載なし`, or `定量効果なし` when information is missing.
4. MUST preserve the flow: `現状 -> 課題 -> 解決 -> 価値`.
5. `## 価値` MUST include a number, a comparison, or `定量効果なし`.
6. If a section exceeds the character limit, summarize it again. Do not add a new section.
7. MUST write each section as prose paragraphs, not bullet lists.
8. MUST NOT start section content lines with `-`, `*`, numbered list markers, or checklist markers.

## Required Output Template

Keep this Japanese template exactly.

```md
# タイトル

## 要約
本文を1段落で記載する。

## 現状
本文を1段落で記載する。

## 課題
本文を1段落で記載する。

## 解決
本文を1段落で記載する。

## 価値
本文を1段落で記載する。
```

## Character Limits

- タイトル: 30 Japanese characters or less
- 要約: 300 Japanese characters or less
- 現状: 300 Japanese characters or less
- 課題: 400 Japanese characters or less
- 解決: 400 Japanese characters or less
- 価値: 300 Japanese characters or less

## Section Rules

### 要約

- Summarize the whole document in one short prose paragraph.
- Include current state, issue, solution, and value.

### 現状

- Compress background, market/domain state, and operational facts.
- Avoid detailed topic-by-topic explanations.

### 課題

- Include only problems that directly follow from the current state.
- If there are multiple issues, group them by importance.

### 解決

- Include only actions that answer the issues.
- Use terms such as OSS, AI, LLM, fine-tuning, rule-based, or production use only if they appear in the input.
- Do not write a technology introduction unrelated to the issues.

### 価値

- Prefer reduction rate, saved time, accuracy, count, cost, or other numeric evidence.
- If there is no number, use a comparison.
- If there is no number or comparison, write `定量効果なし`.

## Workflow

1. Extract topic, current state, issues, solution, value, numbers, and URLs from the input.
2. Assign each extracted item to one of the five sections.
3. Fill the fixed template with prose paragraphs, not bullets.
4. Re-summarize any section that exceeds the character limit.
5. Check that no information outside the input was added.
6. Remove bullet markers if any section starts with `-`, `*`, `1.`, or checklist syntax.

## Completion Checks

- The output has only `# タイトル` and the five required `##` headings.
- The five section names and order match the template.
- Each section body is prose, not a bullet list.
- No section content line starts with `-`, `*`, a numbered list marker, or checklist syntax.
- Every section is within the character limit.
- `## 価値` has a number, comparison, or `定量効果なし`.
- There are no footnotes, citation IDs, reference IDs, or `file:///` links.
- There is no information absent from the source report or notes.

## Do Not

- Do not add, remove, merge, split, or reorder sections.
- Do not use bullet lists, numbered lists, or checklists in the A4 summary body.
- Do not invent facts, numbers, links, or impact.
- Do not exceed character limits.
- Do not write value without quantitative evidence, comparison, or `定量効果なし`.
- Do not use footnotes, citation IDs, or reference IDs.
