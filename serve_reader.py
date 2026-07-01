from __future__ import annotations

import argparse
import functools
import http.server
import socketserver
import sys
import webbrowser
from pathlib import Path


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766
DEFAULT_READER = "output/reader.html"


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def ensure_inside(path: Path, root: Path) -> None:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as error:
        raise SystemExit(f"Path must stay inside the project folder: {path}") from error


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preview the generated local Markdown/TXT review reader over 127.0.0.1."
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="Bind host. Defaults to 127.0.0.1.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Bind port. Defaults to 8766.")
    parser.add_argument("--root", default=".", help="Folder to serve. Defaults to the current project folder.")
    parser.add_argument("--reader", default=DEFAULT_READER, help="Reader path under --root.")
    parser.add_argument("--no-open", action="store_true", help="Start the server without opening a browser.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    reader_path = (root / args.reader).resolve()
    ensure_inside(reader_path, root)
    if not reader_path.exists():
        raise SystemExit(f"Reader file does not exist: {reader_path}")

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    url = f"http://{args.host}:{args.port}/{reader_path.relative_to(root).as_posix()}"

    with ReusableTCPServer((args.host, args.port), handler) as httpd:
        print(f"Serving {root}")
        print(f"Reader: {url}")
        print("Press Ctrl+C to stop.")
        if not args.no_open:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
