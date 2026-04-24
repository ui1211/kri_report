# research-report-kri Workflow

Use this workflow to create or update Japanese research reports with two outputs:

- `{topic}_レポート.md`
- `{topic}_A4_要約.md`

The control instructions are in English for stability with small/local models. The generated report, A4 summary, filenames, headings, and fixed labels must remain Japanese.

## Required Skills

Use these skills:

- `research-report`: end-to-end research, validation, report, and A4 summary workflow
- `report-format-kri`: fixed 10-section Japanese report
- `report-format-a4`: fixed 5-section Japanese A4 summary
- `report-fact-check`: factual, link, structure, and issue-ID validation

Do not use the old `report-format` skill for new report output.

## Task Mode

Infer the task mode from the user request.

- New report: research the topic and create both output files.
- Existing report update: read the existing document, update facts only when needed, and regenerate both output files.
- Format-only: do not perform external search; reformat only the provided material.

If the user does not specify the mode:

- If the input is an existing document, use existing report update.
- If the input is only a topic, use new report.
- If the user says "format only", "整形のみ", or "検索不要", use format-only.

Do not stop only to ask for mode unless the request is genuinely unsafe or impossible to infer.

## Input Types

Accept any of these:

- Topic name
- Search results
- Research notes
- Existing Markdown report
- URLs and source excerpts

## Research Rules

Skip this section for format-only tasks.

1. Search from at least three angles.
2. Prefer official documentation, papers, GitHub, vendor technical documents, standards, and government sources.
3. Use third-party sources to cross-check major claims when possible.
4. Prefer primary sources for numbers, dates, specifications, benchmarks, and production examples.
5. If evidence is insufficient, write `不明`.

Useful query angles:

- `{topic}`
- `{topic} OSS`
- `{topic} benchmark`
- `{topic} case study`
- `{topic} limitation`
- `{topic} architecture`

## Source Evaluation

Classify sources before writing:

- High: official documents, papers, standards, GitHub repositories, technical vendor documents, government documents
- Medium: technical media, specialist blogs, case-study articles
- Low: unsourced pages, reposted content, social media, advertising-heavy pages

Do not rely only on low-quality sources for important claims.

## Main Workflow

1. Determine task mode.
2. Collect input material and sources.
3. Extract topic, URLs, numbers, dates, current-state facts, issues, solutions, and value claims.
4. Extract comparable metrics such as stars, license, cost, accuracy, speed, dates, benchmark scores, and links.
5. Run `report-fact-check` criteria on important facts before writing.
6. Generate `{topic}_レポート.md` with `report-format-kri`.
7. Validate the report with `report-fact-check`.
8. Generate `{topic}_A4_要約.md` with `report-format-a4`, using only the validated report as input.
9. Validate the A4 summary with `report-fact-check`.
10. Update `plan/CHANGELOG.md` when the workflow or skill design changed, not for ordinary report content changes.

## Main Report Requirements

The main report must follow the `report-format-kri` structure exactly.

Required Japanese sections:

```md
# レポート

## 1. メタ情報
## 2. 概要
## 3. 現状
## 4. 課題
## 5. AI解決
## 6. 価値
## 7. トピック一覧
## 8. 比較まとめ
## 9. 更新履歴
## 10. 参考リンク一覧
```

Rules:

- Keep all headings in Japanese.
- Use inline Markdown links only.
- Do not use footnotes, reference IDs, citation IDs, or `[参照: ...]`.
- Assign issues as `C1`, `C2`, `C3`.
- Reuse issue IDs in `AI解決` and `価値`.
- Preserve `現状 -> 課題 -> AI解決 -> 価値`.
- Make `## 8. 比較まとめ` primarily table-based.
- Put fine-grained topic details into comparison table columns instead of long bullet lists.
- When GitHub repositories are included, summarize repository name, link, stars, license, last update if available, and overview in a Markdown table.
- When numeric values exist, put them in comparison tables instead of leaving them only in prose.
- Use `不明` for missing table values. Do not guess.

## A4 Summary Requirements

The A4 summary must follow the `report-format-a4` structure exactly.

Required Japanese sections:

```md
# タイトル

## 要約
## 現状
## 課題
## 解決
## 価値
```

Rules:

- Use only facts from the validated main report.
- Do not add new information.
- Write each section as prose paragraphs, not bullet lists.
- Do not start A4 section content with `-`, `*`, numbered list markers, or checklist markers.
- Keep the output short enough for an A4-style summary.
- `## 価値` must include a number, comparison, or `定量効果なし`.

## Update Rules

For existing report updates:

- Update facts only when new facts, changed numbers, dead links, or better sources exist.
- Preserve valid inline links.
- Convert old footnotes, reference IDs, or citation IDs into inline Markdown links.
- Do not rewrite purely for style if the facts and structure are already correct.
- Add one update line to the main report's `## 9. 更新履歴`.

## Re-search Conditions

Perform more research when:

- An important claim has only one weak source.
- Numbers conflict across sources.
- A source is unclear or unavailable.
- A technical explanation is too shallow.
- The topic granularity is inconsistent.

Do not perform more research for format-only tasks.

## Completion Checks

Finish only when all are true:

- `{topic}_レポート.md` exists.
- `{topic}_A4_要約.md` exists.
- The main report has exactly the required 10 Japanese sections.
- The A4 summary has exactly the required 5 Japanese sections.
- The A4 summary is written as prose paragraphs, not bullet lists.
- Body links and `## 10. 参考リンク一覧` are consistent.
- `## 8. 比較まとめ` is primarily table-based, and detailed topic comparisons are contained in tables.
- GitHub repositories have stars, links, license, and overview in a table, with `不明` for missing values.
- No footnotes, reference IDs, citation IDs, or `file:///` links remain.
- `report-fact-check` has no high-severity unresolved issues.
- The A4 summary contains no information absent from the main report.

## Do Not

- Do not translate Japanese headings or fixed labels.
- Do not create extra report sections.
- Do not invent facts, effects, numbers, dates, links, papers, or products.
- Do not force user confirmation when safe defaults are available.
- Do not use reference IDs or footnotes.
- Do not add ordinary report-content changes to `plan/CHANGELOG.md`; reserve it for skill/workflow design changes.
