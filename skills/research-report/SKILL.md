---
name: research-report
description: Use this workflow to create or update Japanese research reports (調査レポート, レポート作成, A4要約). It performs research, source evaluation, fact checking, a fixed 10-section report via report-format-kri, and a fixed 5-section A4 summary via report-format-a4.
---

# research-report

## Purpose

Create or update two Japanese Markdown files:

- `{topic}_レポート.md`: a 10-section report that follows `report-format-kri`
- `{topic}_A4_要約.md`: a 5-section A4-style summary that follows `report-format-a4`

The final outputs must be written in Japanese. Keep all required Japanese headings and labels unchanged.

## Use These Skills

- `report-format-kri`: format the main 10-section Japanese report.
- `report-format-a4`: summarize the validated report into a 5-section Japanese A4 summary.
- `report-fact-check`: validate facts, links, numbers, structure, and issue-ID consistency.

Do not use the old `report-format` skill for new work. If old reports mention it, migrate the output to `report-format-kri`.

## Task Mode

Infer the task mode from the user request.

- New report: research the topic and create both files.
- Existing report update: read the existing material, research only if needed, and update both files.
- Format-only: do not perform external search; format only the provided material.

If the mode is unclear, use this default:

- If the user provides an existing document, treat it as an existing report update.
- If the user provides only a topic, treat it as a new report.

## Research Rules

Run web research only when the user request allows or requires it.

1. Search from at least three angles.
2. Combine official sources, papers, GitHub, vendor documents, and third-party sources.
3. Prefer primary sources for numbers, dates, specifications, benchmarks, and case studies.
4. Cross-check important claims with at least two sources when possible.
5. Write `不明` when evidence is insufficient.

Useful query angles:

- `{topic}`
- `{topic} OSS`
- `{topic} benchmark`
- `{topic} case study`
- `{topic} limitation`

## Workflow

1. Determine the task mode.
2. Extract topic, URLs, numbers, issues, solutions, and value claims from input or research results.
3. Validate numbers, dates, claims, and link quality using the `report-fact-check` criteria.
4. Create the 10-section report with `report-format-kri`.
5. Run `report-fact-check` again on the report.
6. Create the A4 summary with `report-format-a4`, using only the validated report as input.
7. Validate both outputs before finishing.

## Update Rules

- Update content only when new facts, changed numbers, dead links, or better sources exist.
- If the facts are unchanged, limit changes to structure, clarity, and link consistency.
- Preserve valid inline links.
- Convert old footnotes, reference IDs, or citation IDs into normal inline Markdown links.
- Add one line to `## 9. 更新履歴` with the date and update summary.

## Output Requirements

Both files must be produced unless the user explicitly asks for only one.

- The main report must match the `report-format-kri` 10-section structure.
- The A4 summary must contain only the five `report-format-a4` sections.
- Body links and `## 10. 参考リンク一覧` must be consistent.
- The A4 summary must not contain facts absent from the main report.
- Do not include footnotes, citation IDs, reference IDs, or `file:///` links.

## Completion Checks

- `{topic}_レポート.md` exists.
- `{topic}_A4_要約.md` exists.
- The report has `## 1. メタ情報` through `## 10. 参考リンク一覧`.
- The A4 summary has `## 要約`, `## 現状`, `## 課題`, `## 解決`, and `## 価値`.
- No high-severity `report-fact-check` issue remains.
- If research was performed, important numbers, dates, and claims have evidence links.
