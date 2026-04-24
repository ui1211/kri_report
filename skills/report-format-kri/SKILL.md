---
name: report-format-kri
description: Use this skill to format research notes, search results, or existing drafts into a Japanese Markdown report (レポート作成, 調査レポート). The output must be Japanese and must follow the fixed 10-section structure, inline Markdown links, C1/C2 issue IDs, and the 現状→課題→AI解決→価値 reasoning flow.
---

# report-format-kri

## Purpose

Format the input into a Japanese Markdown report.

Use only the information provided by the user or collected by the calling workflow. This skill formats and rewrites; it does not decide whether web research is allowed. Use `research-report` when research is required. Use `report-fact-check` when validation is required.

The final output must be written in Japanese. Do not translate the required Japanese headings or labels.

## Core Rules

1. MUST keep exactly the 10 required sections.
2. MUST NOT change Japanese section headings, section order, or numbering.
3. MUST use normal inline Markdown links: `[text](https://example.com)`.
4. MUST NOT use footnotes, reference IDs, citation IDs, or `[参照: ...]`.
5. MUST NOT invent facts, numbers, effects, products, papers, or links.
6. If evidence is missing, write `不明` or `該当なし`.
7. MUST assign issue IDs as `C1`, `C2`, `C3` in `## 4. 課題`.
8. MUST reuse the same issue IDs in `## 5. AI解決` and `## 6. 価値`.
9. MUST preserve the reasoning flow: `現状 -> 課題 -> AI解決 -> 価値`.
10. MUST include at least one of these for value: number, comparison, or evidence link.

## Input Extraction

Before writing, extract the following from the input:

- Topic
- Creation or update date
- Main topics
- URLs
- Numbers, specifications, and dates
- Current-state facts
- Issues
- AI, OSS, research, or production examples
- Quantified effects or comparison points

Do not fill missing items with guesses. Put `不明` or `該当なし` in the template when required information is missing.

## Required Output Template

The output must follow this template exactly. Keep the Japanese headings and labels unchanged.

```md
# レポート

## 1. メタ情報
- 作成日時: YYYY-MM-DD
- 入力概要:
- トピック数:

## 2. 概要
- 

## 3. 現状
- 業界・領域全体の状況:
- 実運用事例:

## 4. 課題
- C1:
- C2:

## 5. AI解決
- C1対応:
  - OSS:
  - 研究:
  - 実運用:
- C2対応:
  - OSS:
  - 研究:
  - 実運用:

## 6. 価値
- C1由来:
- C2由来:

## 7. トピック一覧
### {トピック名}
- 概要: [説明テキスト](https://example.com/path)
- 特徴:
  - 
- 主要スペック or 数値:
- 制約 or 注意点:

## 8. 比較まとめ
- 比較軸:
  - 精度
  - コスト
  - 導入難易度
  - 拡張性
- 違い:
- 使い分け:
- 強み / 弱み:

## 9. 更新履歴
- YYYY-MM-DD: 初版

## 10. 参考リンク一覧
- [記事タイトル](https://example.com/path)
```

## Section Rules

### 1. メタ情報

- `作成日時` must use `YYYY-MM-DD`.
- `入力概要` must be one concise line.
- `トピック数` must equal the number of `###` topics in `## 7. トピック一覧`.

### 2. 概要

- Summarize the whole report in one or more bullets.
- Include all four elements: current state, issue, AI solution, and value.

### 3. 現状

- Describe the macro-level industry or domain situation.
- Move detailed product or technology descriptions to `## 7. トピック一覧`.
- Include operational examples, observed facts, or public evidence with inline links.

### 4. 課題

- Include only issues that directly follow from the current state.
- Use `C1`, `C2`, `C3` as consecutive IDs.
- Prefer issues about AI accuracy, labor shortage, cost, data shortage, and operational burden.

### 5. AI解決

- Map each solution block to an issue ID, such as `C1対応`.
- Keep the sublabels `OSS`, `研究`, and `実運用`.
- Write `該当なし` or `不明` when a category has no evidence.
- Do not list solutions that do not address the issue.

### 6. 価値

- Map each value block to an issue ID, such as `C1由来`.
- Prefer reduction rate, saved time, accuracy, count, cost, or other numeric evidence.
- If no number exists, use comparison or an evidence link.
- Do not write unsupported effects.

### 7. トピック一覧

- Keep topic granularity consistent: technology, product, OSS, paper, or case study.
- Start every topic with `### {トピック名}`.
- Put at least one inline link in `概要`.
- Put at least one child bullet under `特徴`.

### 8. 比較まとめ

- Keep the four fixed comparison axes: `精度`, `コスト`, `導入難易度`, `拡張性`.
- Compare all topics using the same criteria.
- Write `不明` when comparison evidence is missing.

### 9. 更新履歴

- For a new report, write `YYYY-MM-DD: 初版`.
- For an update, write `YYYY-MM-DD: {更新内容}`.

### 10. 参考リンク一覧

- List only URLs used in inline body links.
- Do not add URLs that do not appear in the body.
- Do not use local file links, footnotes, or reference IDs.

## Workflow

1. Read the input and extract URLs, numbers, dates, topics, and issue candidates.
2. Build the macro-level `## 3. 現状`.
3. Derive issues from the current state and assign `C1`, `C2`, `C3`.
4. Classify solutions for each issue under `OSS`, `研究`, and `実運用`.
5. Write value for each issue ID.
6. Organize individual topics in `## 7. トピック一覧`.
7. Write `## 8. 比較まとめ` using the fixed axes.
8. Make body links and `## 10. 参考リンク一覧` consistent.
9. Revise until all completion checks pass.

## Completion Checks

- `# レポート` exists.
- `## 1` through `## 10` exist in the required order.
- All Japanese headings match the template.
- `## 4. 課題` uses `C1`, `C2`, `C3` issue IDs.
- `## 5. AI解決` and `## 6. 価値` reuse the same issue IDs.
- The reasoning flow is `現状 -> 課題 -> AI解決 -> 価値`.
- Every topic summary has at least one inline link.
- The reference link list matches body links.
- There are no footnotes, citation IDs, reference IDs, or `file:///` links.

## Do Not

- Do not add, remove, merge, split, or reorder sections.
- Do not invent facts, numbers, links, or impact.
- Do not use unsupported speculation.
- Do not list solutions unrelated to issue IDs.
- Do not use footnotes, citations IDs, or reference IDs.
