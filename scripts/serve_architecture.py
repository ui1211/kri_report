from __future__ import annotations

import argparse
import functools
import http.server
import socketserver
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReusableTcpServer(socketserver.TCPServer):
    allow_reuse_address = True


class Utf8RequestHandler(http.server.SimpleHTTPRequestHandler):
    utf8_suffixes = {".html", ".json", ".md"}

    def guess_type(self, path: str) -> str:
        content_type = super().guess_type(path)
        if Path(path).suffix.lower() in self.utf8_suffixes and "charset=" not in content_type:
            return f"{content_type}; charset=utf-8"
        return content_type


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve architecture.html locally.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    handler = functools.partial(Utf8RequestHandler, directory=ROOT)

    for port in range(args.port, args.port + 20):
        try:
            server = ReusableTcpServer((args.host, port), handler)
            break
        except OSError:
            continue
    else:
        raise OSError(f"No available port from {args.port} to {args.port + 19}")

    with server:
        url = f"http://{args.host}:{port}/docs/architecture.html"
        print(f"Serving {ROOT}")
        print(f"Open {url}")
        if not args.no_browser:
            webbrowser.open(url)
        server.serve_forever()


if __name__ == "__main__":
    main()
