from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HTML = ROOT / "docs" / "architecture.html"
DEFAULT_DATA = ROOT / "docs" / "architecture.generated.json"
DEFAULT_OUTPUT_DIR = ROOT / "dist"


def default_output_path() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return DEFAULT_OUTPUT_DIR / f"architecture_snapshot_{timestamp}.html"


def load_json_text(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def embed_data(html: str, data_text: str) -> str:
    safe_data_text = data_text.replace("</", "<\\/")
    script_tag = (
        '  <script id="architecture-data-json" type="application/json">\n'
        f"{safe_data_text}\n"
        "  </script>\n"
    )
    if 'id="architecture-data-json"' in html:
        raise ValueError("HTML already contains an embedded architecture data script.")
    html = html.replace("  <script>\n", f"{script_tag}  <script>\n", 1)

    lines = html.splitlines(keepends=True)
    output: list[str] = []
    skip_next_response_check = False
    replaced_fetch = False
    replaced_json = False

    for line in lines:
        if 'const response = await fetch("architecture.generated.json"' in line:
            indent = line[: len(line) - len(line.lstrip())]
            output.append(
                f'{indent}const embeddedData = document.getElementById("architecture-data-json");\n'
            )
            output.append(f"{indent}state.data = JSON.parse(embeddedData.textContent);\n")
            skip_next_response_check = True
            replaced_fetch = True
            continue
        if skip_next_response_check and "if (!response.ok)" in line:
            skip_next_response_check = False
            continue
        if "state.data = await response.json();" in line:
            replaced_json = True
            continue
        output.append(line)

    if not replaced_fetch or not replaced_json:
        raise ValueError("Could not find the architecture data fetch block to replace.")

    return "".join(output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a single-file distributable architecture viewer HTML."
    )
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = args.output or default_output_path()
    html = args.html.read_text(encoding="utf-8")
    data_text = load_json_text(args.data)
    packaged_html = embed_data(html, data_text)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(packaged_html, encoding="utf-8", newline="\n")
    print(f"Packaged {output_path}")


if __name__ == "__main__":
    main()
