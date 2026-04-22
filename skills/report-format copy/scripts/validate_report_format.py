from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPORT_TITLE = "# レポート"
SECTION_HEADERS = [
    "## 1. メタ情報",
    "## 2. 概要（全体）",
    "## 3. トピック一覧",
    "## 4. 比較まとめ",
    "## 5. 更新履歴",
    "## 6. 参考リンク一覧",
]
TOPIC_REQUIRED_PREFIXES = [
    "- 概要:",
    "- 特徴:",
    "- 主要スペック or 数値:",
    "- 制約 or 注意点:",
]
COMPARISON_REQUIRED_PREFIXES = [
    "- 違い:",
    "- 使い分け:",
    "- 強み / 弱み:",
]
TOPIC_HEADER_RE = re.compile(r"^###\s+.+$")
WEB_LINK_RE = re.compile(r"\[[^\]]+\]\((https?://[^)\s]+)\)")
LIST_LINK_RE = re.compile(r"^-\s+\[([^\]]+)\]\((https?://[^)\s]+)\)\s*$")
LEGACY_FOOTNOTE_RE = re.compile(r"\[\^[A-Za-z0-9._-]+\]")
INLINE_REF_RE = re.compile(r"\[参照:\s*[^\]]+\]\(#[^)]+\)")
FILE_LINK_RE = re.compile(r"\[[^\]]+\]\((file:///[^)\s]+)\)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def validate_report(text: str) -> list[str]:
    lines = text.splitlines()
    errors: list[str] = []

    if not lines:
        return ["レポートが空です。"]

    if lines[0].strip() != REPORT_TITLE:
        errors.append("先頭行は '# レポート' でなければなりません。")

    cleaned_text = INLINE_CODE_RE.sub("", text)
    if LEGACY_FOOTNOTE_RE.search(cleaned_text):
        errors.append("Markdown 脚注構文 '[^...]' は使用できません。")
    if INLINE_REF_RE.search(cleaned_text):
        errors.append("注釈記法 '[参照: ...](#...)' は使用できません。")
    if FILE_LINK_RE.search(cleaned_text):
        errors.append("'file:///' リンクは使用できません。")

    header_positions: list[int] = []
    for header in SECTION_HEADERS:
        matches = [idx for idx, line in enumerate(lines) if line.strip() == header]
        if len(matches) != 1:
            errors.append(f"見出し '{header}' は 1 回だけ存在する必要があります。")
        elif header_positions and matches[0] <= header_positions[-1]:
            errors.append("固定セクションの順序が崩れています。")
            header_positions.append(matches[0])
        elif matches:
            header_positions.append(matches[0])

    if len(header_positions) != len(SECTION_HEADERS):
        return errors

    sections = _slice_sections(lines, header_positions)
    errors.extend(_validate_topics(sections["## 3. トピック一覧"]))
    errors.extend(_validate_comparison_section(sections["## 4. 比較まとめ"]))
    errors.extend(_validate_source_list(sections["## 6. 参考リンク一覧"], cleaned_text))
    return errors


def _slice_sections(lines: list[str], positions: list[int]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    for index, header in enumerate(SECTION_HEADERS):
        start = positions[index] + 1
        end = positions[index + 1] if index + 1 < len(positions) else len(lines)
        sections[header] = lines[start:end]
    return sections


def _validate_topics(lines: list[str]) -> list[str]:
    errors: list[str] = []
    topic_indices = [idx for idx, line in enumerate(lines) if TOPIC_HEADER_RE.match(line.strip())]
    if not topic_indices:
        return ["'## 3. トピック一覧' に少なくとも 1 件のトピックが必要です。"]

    for topic_number, start in enumerate(topic_indices):
        end = topic_indices[topic_number + 1] if topic_number + 1 < len(topic_indices) else len(lines)
        block = [line.rstrip() for line in lines[start:end] if line.strip()]
        topic_title = block[0] if block else f"topic-{topic_number + 1}"
        errors.extend(_validate_topic_block(topic_title, block))
    return errors


def _validate_topic_block(topic_title: str, block: list[str]) -> list[str]:
    errors: list[str] = []
    prefixes_present = {prefix: False for prefix in TOPIC_REQUIRED_PREFIXES}

    for line in block[1:]:
        stripped = line.strip()
        for prefix in TOPIC_REQUIRED_PREFIXES:
            if stripped.startswith(prefix):
                prefixes_present[prefix] = True

    for prefix, present in prefixes_present.items():
        if not present:
            errors.append(f"{topic_title} に '{prefix}' がありません。")

    summary_line = next((line.strip() for line in block[1:] if line.strip().startswith("- 概要:")), "")
    if not WEB_LINK_RE.search(summary_line):
        errors.append(f"{topic_title} の '- 概要:' には通常の本文リンクが必要です。")

    feature_index = next((idx for idx, line in enumerate(block) if line.strip().startswith("- 特徴:")), -1)
    if feature_index == -1:
        return errors

    has_feature_child = False
    for line in block[feature_index + 1 :]:
        stripped = line.strip()
        if stripped.startswith("- 主要スペック or 数値:") or stripped.startswith("- 制約 or 注意点:"):
            break
        if stripped.startswith("- ") and line.startswith("  "):
            has_feature_child = True
            break
    if not has_feature_child:
        errors.append(f"{topic_title} の '- 特徴:' の下に子箇条書きが必要です。")

    return errors


def _validate_comparison_section(lines: list[str]) -> list[str]:
    errors: list[str] = []
    stripped_lines = [line.strip() for line in lines if line.strip()]
    for prefix in COMPARISON_REQUIRED_PREFIXES:
        if not any(line.startswith(prefix) for line in stripped_lines):
            errors.append(f"'## 4. 比較まとめ' に '{prefix}' がありません。")
    return errors


def _validate_source_list(source_lines: list[str], cleaned_text: str) -> list[str]:
    errors: list[str] = []
    source_entries: list[str] = []

    for line in source_lines:
        stripped = line.strip()
        if not stripped:
            continue
        match = LIST_LINK_RE.match(stripped)
        if not match:
            errors.append(f"'## 6. 参考リンク一覧' の形式が不正です: {stripped}")
            continue
        source_entries.append(match.group(2))

    if not source_entries:
        errors.append("'## 6. 参考リンク一覧' に少なくとも 1 件のリンクが必要です。")
        return errors

    body_text = cleaned_text.split("## 6. 参考リンク一覧", 1)[0]
    body_urls = WEB_LINK_RE.findall(body_text)
    if not body_urls:
        errors.append("本文内に通常リンクがありません。")
        return errors

    unique_body_urls = []
    for url in body_urls:
        if url not in unique_body_urls:
            unique_body_urls.append(url)

    for url in source_entries:
        if source_entries.count(url) > 1:
            errors.append(f"参考リンク一覧で URL が重複しています: {url}")
            break

    missing = [url for url in unique_body_urls if url not in source_entries]
    unused = [url for url in source_entries if url not in unique_body_urls]
    for url in missing:
        errors.append(f"本文で使われている URL が参考リンク一覧にありません: {url}")
    for url in unused:
        errors.append(f"参考リンク一覧にある URL が本文で使われていません: {url}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the report-format Markdown contract.")
    parser.add_argument("report", type=Path, help="Path to a Markdown report")
    args = parser.parse_args(argv)

    text = args.report.read_text(encoding="utf-8")
    errors = validate_report(text)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("OK: report-format contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
