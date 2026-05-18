from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "report" / "00_top.md"
DEFAULT_BASE = ROOT / "docs" / "architecture.json"
DEFAULT_OUTPUT = ROOT / "docs" / "architecture.generated.json"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
MERMAID_NODE_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\[([^\]]+)\]\s*$")
MERMAID_EDGE_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*---\s*([A-Za-z0-9_]+)\s*$")
MERMAID_SUBGRAPH_RE = re.compile(r"^\s*subgraph\s+([A-Za-z0-9_]+)\[([^\]]+)\]\s*$")


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    parts = text.split("---", 2)
    if len(parts) == 3:
        return parts[2].lstrip()
    return text


def slugify(value: str) -> str:
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    safe = re.sub(r"[^0-9A-Za-z_-]+", "-", value).strip("-").lower()
    return safe or f"section-{digest}"


def split_table_row(line: str) -> list[str]:
    cells = line.strip().strip("|").split("|")
    return [cell.strip() for cell in cells]


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def parse_table(lines: list[str], start: int) -> tuple[dict[str, Any] | None, int]:
    if start + 1 >= len(lines) or not is_table_separator(lines[start + 1]):
        return None, start

    headers = split_table_row(lines[start])
    rows: list[dict[str, str]] = []
    index = start + 2

    while index < len(lines) and lines[index].lstrip().startswith("|"):
        values = split_table_row(lines[index])
        if len(values) < len(headers):
            values.extend([""] * (len(headers) - len(values)))
        rows.append(dict(zip(headers, values[: len(headers)])))
        index += 1

    return {"headers": headers, "rows": rows}, index


def parse_sections(markdown: str) -> list[dict[str, Any]]:
    lines = strip_frontmatter(markdown).splitlines()
    sections: list[dict[str, Any]] = []
    seen_ids: dict[str, int] = {}
    current: dict[str, Any] | None = None
    code_fence = False
    code_lang = ""
    code_lines: list[str] = []
    paragraph: list[str] = []
    index = 0

    def ensure_section() -> dict[str, Any]:
        nonlocal current
        if current is None:
            current = {
                "id": "intro",
                "level": 1,
                "title": "冒頭",
                "blocks": [],
                "text": "",
            }
            sections.append(current)
        return current

    def flush_paragraph() -> None:
        nonlocal paragraph
        if not paragraph:
            return
        section = ensure_section()
        content = "\n".join(paragraph).strip()
        section["blocks"].append({"type": "paragraph", "text": content})
        section["text"] += f"\n{content}"
        paragraph = []

    while index < len(lines):
        line = lines[index]

        if line.startswith("```"):
            if code_fence:
                section = ensure_section()
                content = "\n".join(code_lines)
                section["blocks"].append(
                    {"type": "code", "language": code_lang, "text": content}
                )
                section["text"] += f"\n{content}"
                code_fence = False
                code_lang = ""
                code_lines = []
            else:
                flush_paragraph()
                code_fence = True
                code_lang = line.strip("`").strip()
            index += 1
            continue

        if code_fence:
            code_lines.append(line)
            index += 1
            continue

        heading = HEADING_RE.match(line)
        if heading:
            flush_paragraph()
            title = heading.group(2).strip()
            section_id = slugify(title)
            seen_ids[section_id] = seen_ids.get(section_id, 0) + 1
            if seen_ids[section_id] > 1:
                section_id = f"{section_id}-{seen_ids[section_id]}"
            current = {
                "id": section_id,
                "level": len(heading.group(1)),
                "title": title,
                "blocks": [],
                "text": title,
            }
            sections.append(current)
            index += 1
            continue

        if line.lstrip().startswith("|"):
            table, next_index = parse_table(lines, index)
            if table:
                flush_paragraph()
                section = ensure_section()
                section["blocks"].append({"type": "table", **table})
                section["text"] += "\n" + json.dumps(table, ensure_ascii=False)
                index = next_index
                continue

        if not line.strip():
            flush_paragraph()
            index += 1
            continue

        paragraph.append(line)
        index += 1

    flush_paragraph()
    return sections


def parse_mermaid_graph(text: str, graph_id: str, title: str) -> dict[str, Any]:
    nodes: dict[str, dict[str, str]] = {}
    edges: list[dict[str, str]] = []
    current_group = ""

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("flowchart"):
            continue
        if stripped == "end":
            current_group = ""
            continue

        subgraph = MERMAID_SUBGRAPH_RE.match(line)
        if subgraph:
            current_group = subgraph.group(2)
            continue

        node = MERMAID_NODE_RE.match(line)
        if node:
            node_id, label = node.groups()
            nodes[node_id] = {
                "id": node_id,
                "label": label,
                "group": current_group or "未分類",
            }
            continue

        edge = MERMAID_EDGE_RE.match(line)
        if edge:
            source, target = edge.groups()
            edges.append({"source": source, "target": target})
            for node_id in (source, target):
                nodes.setdefault(
                    node_id,
                    {"id": node_id, "label": node_id, "group": "未分類"},
                )

    return {
        "id": graph_id,
        "title": title,
        "nodes": list(nodes.values()),
        "edges": edges,
    }


def collect_mermaid_graphs(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    graphs: list[dict[str, Any]] = []
    for section in sections:
        for block_index, block in enumerate(section["blocks"]):
            if block.get("type") != "code" or block.get("language") != "mermaid":
                continue
            graph_id = f"{section['id']}-graph-{block_index}"
            block["graphId"] = graph_id
            graphs.append(parse_mermaid_graph(block["text"], graph_id, section["title"]))
    return graphs


def extract_links(markdown: str) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    links: list[dict[str, str]] = []
    for label, href in LINK_RE.findall(markdown):
        key = (label, href)
        if key in seen:
            continue
        seen.add(key)
        links.append({"label": label, "href": href})
    return links


def find_section(sections: list[dict[str, Any]], title: str) -> dict[str, Any] | None:
    for section in sections:
        if section["title"] == title:
            return section
    return None


def section_tables(section: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not section:
        return []
    return [block for block in section["blocks"] if block["type"] == "table"]


def markdown_key_from_href(href: str) -> str:
    return unquote(href.split("#", 1)[0]).replace("\\", "/")


def local_markdown_path(href: str) -> Path | None:
    if href.startswith(("http://", "https://", "#")):
        return None
    clean_href = unquote(href.split("#", 1)[0])
    path = (ROOT / "report" / clean_href).resolve()
    try:
        path.relative_to(ROOT / "report")
    except ValueError:
        return None
    if path.suffix.lower() != ".md" or not path.exists():
        return None
    return path


def markdown_links_in(value: str) -> list[dict[str, str]]:
    return [{"label": label, "href": href} for label, href in LINK_RE.findall(value)]


def collect_report_docs(markdown: str) -> dict[str, Any]:
    reports: dict[str, Any] = {}
    for link in extract_links(markdown):
        label = link["label"]
        href = link["href"]
        path = local_markdown_path(href)
        if path is None:
            continue
        key = str(path.relative_to(ROOT / "report")).replace("\\", "/")
        if key in reports:
            continue
        content = path.read_text(encoding="utf-8")
        sections = parse_sections(content)
        reports[key] = {
            "label": label,
            "path": key,
            "raw": strip_frontmatter(content),
            "sections": sections,
            "links": extract_links(content),
        }
    return reports


def add_tag(tags: dict[str, dict[str, str]], tag_type: str, label: str) -> str:
    tag_id = f"{tag_type}:{slugify(label)}"
    tags.setdefault(
        tag_id,
        {
            "id": tag_id,
            "label": label,
            "type": tag_type,
        },
    )
    return tag_id


def add_edge(
    edges: set[tuple[str, str, str]],
    source: str,
    target: str,
    edge_type: str,
) -> None:
    if source and target and source != target:
        edges.add((source, target, edge_type))


def table_links_to_report_keys(value: str) -> list[str]:
    keys: list[str] = []
    for link in markdown_links_in(value):
        path = local_markdown_path(link["href"])
        if path is None:
            continue
        keys.append(str(path.relative_to(ROOT / "report")).replace("\\", "/"))
    return keys


def build_document_meta(document_table: dict[str, Any] | None) -> dict[str, dict[str, str]]:
    if not document_table:
        return {}
    meta: dict[str, dict[str, str]] = {}
    for row in document_table["rows"]:
        links = markdown_links_in(row.get("リンク", ""))
        if not links:
            continue
        key = markdown_key_from_href(links[0]["href"])
        meta[key] = {
            "title": row.get("タイトル", key),
            "date": row.get("作成日", ""),
            "summary": row.get("概要", ""),
            "path": key,
        }
    return meta


def infer_domain(title: str, summary: str) -> str:
    text = f"{title} {summary}"
    rules = [
        ("外壁・シーリング", ["外壁", "シーリング", "ひび", "劣化", "建築"]),
        ("漏水・配管", ["漏水", "配管", "センサー", "電源", "ThingSpeak", "IoT"]),
        ("点群・3D", ["点群", "3D", "BIM"]),
        ("横断AI・OSS", ["AI", "OSS", "LLM", "n8n", "ComfyUI", "ハーネス", "アノテーション"]),
        ("全体・市場", ["市場", "調査", "料金", "災害", "環境"]),
    ]
    for domain, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return domain
    return "未分類"


def build_knowledge_graph(
    document_table: dict[str, Any] | None,
    tech_tables: list[dict[str, Any]],
    market_tables: list[dict[str, Any]],
    topic_tables: list[dict[str, Any]],
    reports: dict[str, Any],
) -> dict[str, Any]:
    document_meta = build_document_meta(document_table)
    tags: dict[str, dict[str, str]] = {}
    edges: set[tuple[str, str, str]] = set()
    report_nodes: dict[str, dict[str, Any]] = {}

    for key, report in reports.items():
        meta = document_meta.get(key, {})
        title = meta.get("title") or report.get("label") or key
        summary = meta.get("summary", "")
        domain = infer_domain(title, summary)
        report_id = f"report:{key}"
        report_nodes[report_id] = {
            "id": report_id,
            "key": key,
            "label": title,
            "type": "report",
            "domain": domain,
            "date": meta.get("date", ""),
            "summary": summary,
        }
        domain_id = add_tag(tags, "domain", domain)
        add_edge(edges, report_id, domain_id, "inferred-domain")

    def connect_table(table: dict[str, Any], tag_type: str) -> None:
        if not table or len(table.get("headers", [])) < 2:
            return
        row_header = table["headers"][0]
        domain_headers = table["headers"][1:]
        for row in table["rows"]:
            row_label = row.get(row_header, "").strip()
            if not row_label:
                continue
            row_tag = add_tag(tags, tag_type, row_label)
            for domain in domain_headers:
                cell = row.get(domain, "").strip()
                if not cell or cell == "-":
                    continue
                domain_tag = add_tag(tags, "domain", domain)
                add_edge(edges, row_tag, domain_tag, f"{tag_type}-domain")
                for key in table_links_to_report_keys(cell):
                    report_id = f"report:{key}"
                    add_edge(edges, report_id, row_tag, f"report-{tag_type}")
                    add_edge(edges, report_id, domain_tag, "report-domain")

    for table in tech_tables:
        connect_table(table, "technology")
    for table in market_tables:
        connect_table(table, "market")

    for table in topic_tables:
        for row in table.get("rows", []):
            topic = row.get("トピック案", "").strip()
            if not topic:
                continue
            topic_tag = add_tag(tags, "topic", topic)
            for cell in row.values():
                for key in table_links_to_report_keys(cell):
                    add_edge(edges, f"report:{key}", topic_tag, "report-topic")

    all_nodes = list(report_nodes.values()) + [
        {**tag, "type": tag["type"], "summary": ""} for tag in tags.values()
    ]
    return {
        "nodes": all_nodes,
        "edges": [
            {"source": source, "target": target, "type": edge_type}
            for source, target, edge_type in sorted(edges)
        ],
        "documentMeta": document_meta,
    }


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_data(source: Path, base_path: Path) -> dict[str, Any]:
    markdown = source.read_text(encoding="utf-8")
    sections = parse_sections(markdown)
    mermaid_graphs = collect_mermaid_graphs(sections)
    base = load_json(base_path)
    doc_tables = section_tables(find_section(sections, "ドキュメント一覧"))
    tech_tables = section_tables(find_section(sections, "技術マップ"))
    market_tables = section_tables(find_section(sections, "市場マップ"))
    topic_tables = section_tables(find_section(sections, "関連新規トピックス案"))
    reports = collect_report_docs(markdown)
    knowledge_graph = build_knowledge_graph(
        doc_tables[0] if doc_tables else None,
        tech_tables,
        market_tables,
        topic_tables,
        reports,
    )

    data = {
        **base,
        "generated": {
            "source": str(source.relative_to(ROOT)),
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "sectionCount": len(sections),
            "linkCount": len(extract_links(markdown)),
            "documentCount": len(doc_tables[0]["rows"]) if doc_tables else 0,
        },
        "markdown": {
            "source": str(source.relative_to(ROOT)),
            "raw": strip_frontmatter(markdown),
            "sections": sections,
            "links": extract_links(markdown),
            "documentTable": doc_tables[0] if doc_tables else None,
            "techTables": tech_tables,
            "marketTables": market_tables,
            "topicTables": topic_tables,
            "mermaidGraphs": mermaid_graphs,
            "reports": reports,
            "knowledgeGraph": knowledge_graph,
        },
    }
    data.setdefault("meta", {})
    data["meta"]["title"] = "00_top.md インタラクティブビューア"
    data["meta"]["subtitle"] = (
        "report/00_top.md を起動時に読み取り、表・リンク・本文・構成図を"
        "検索しながら確認するためのローカルビューア"
    )
    data["meta"]["updated"] = data["generated"]["generatedAt"]
    return data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build viewer data from report/00_top.md.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = build_data(args.source, args.base)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Updated {args.output}")


if __name__ == "__main__":
    main()
