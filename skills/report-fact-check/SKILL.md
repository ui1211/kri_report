---
name: report-fact-check
description: Use this skill to validate Japanese research reports and A4 summaries. It checks factual accuracy, numbers, dates, links, source quality, fixed report structure, C1/C2 issue-ID consistency, and missing evidence before or after using report-format-kri or report-format-a4.
---

# report-fact-check

## Purpose

Validate a Japanese report and clearly identify what must be fixed.

This skill is for review and validation only. Do not rewrite the whole report. When fixes are needed, report the issue and send the content back to the relevant formatting skill.

The validation report may be written in Japanese unless the user requests otherwise.

## Targets

- A `report-format-kri` 10-section report
- A `report-format-a4` 5-section summary
- An existing Japanese report
- A draft created from research notes

## Workflow

1. Check structure.
2. Extract claims, numbers, dates, specifications, and comparisons.
3. Check whether each important claim has an inline link or input evidence.
4. Evaluate source quality.
5. Check issue-ID consistency across 課題, AI解決, and 価値.
6. Check consistency between body links and `参考リンク一覧`.
7. Return `OK`, `要修正`, or `不明`.

## Checks

### 1. Structure

- `report-format-kri` output has `## 1. メタ情報` through `## 10. 参考リンク一覧`.
- `report-format-a4` output has only `## 要約`, `## 現状`, `## 課題`, `## 解決`, and `## 価値`.
- No required heading is added, deleted, renamed, or reordered.

### 2. Factuality

- No unsupported assertion is written as fact.
- Inferences are not mixed with verified facts.
- Unverifiable information is marked as `不明`.
- No information outside the input or cited evidence was added.

### 3. Numbers, Dates, and Specifications

- Numbers, dates, specifications, performance, cost, and counts have evidence.
- Units are clear.
- If sources conflict, the adopted value and reason are clear.

### 4. Links

- Body links use normal Markdown links.
- There are no footnotes, citation IDs, reference IDs, `[参照: ...]`, or `file:///` links.
- `参考リンク一覧` matches URLs used in the body.
- `参考リンク一覧` does not contain unused URLs.

### 5. Issue IDs

- Issues use consecutive IDs: `C1`, `C2`, `C3`.
- `AI解決` has matching blocks for each issue ID.
- `価値` has matching blocks for each issue ID.
- No solution or value is unrelated to the issue it claims to address.

### 6. Topic Granularity

- Topic granularity is consistent.
- Technologies, products, companies, papers, and case studies are not mixed without a clear reason.
- All items compared in `比較まとめ` also appear in `トピック一覧`.

## Source Quality

- High: official documentation, papers, standards, GitHub repositories, technical vendor documents, government documents
- Medium: technical media, specialist blogs, case-study articles
- Low: unsourced articles, reposted content, social media, advertising-heavy pages

Claims supported only by low-quality sources should be marked `要修正` or `不明`.

## Required Output Format

Return validation results in this Japanese format.

```md
## ファクトチェック結果

### 総合判定
- 判定: OK / 要修正 / 不明
- 理由:

### 指摘事項
- 重要度: 高 / 中 / 低
- 箇所:
- 問題:
- 修正方針:

### 構造チェック
- report-format-kri / report-format-a4 準拠:
- 見出し:
- 課題 ID:
- リンク整合:

### ソース品質
- 高:
- 中:
- 低:

### 残課題
- 
```

## Decision Rules

- `OK`: no serious structure error, missing evidence, or link inconsistency remains.
- `要修正`: there is a factual, structural, evidence, or link problem that should be fixed.
- `不明`: the input or evidence is insufficient to judge.

## Do Not

- Do not state unsupported fixes as facts.
- Do not mark low-quality-source-only claims as `OK`.
- Do not ignore missing links.
- Do not add information to an A4 summary that is absent from the source report.
