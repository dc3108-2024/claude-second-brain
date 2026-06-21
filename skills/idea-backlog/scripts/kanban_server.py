"""
kanban_server.py — live Kanban board for idea-backlog.

Starts a local HTTP server that regenerates the board on every browser request.
Page auto-refreshes every 30 seconds via meta http-equiv="refresh".

Usage:
    python3 ~/.claude/skills/idea-backlog/scripts/kanban_server.py          # port 8788, 30s refresh
    python3 ~/.claude/skills/idea-backlog/scripts/kanban_server.py --port 9001
    python3 ~/.claude/skills/idea-backlog/scripts/kanban_server.py --refresh 60
"""
import argparse
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from kanban import generate_html, IDEAS_PATH

DEFAULT_PORT = 8788
DEFAULT_REFRESH = 30


def _parse_args():
    parser = argparse.ArgumentParser(description="Live Kanban board server.")
    parser.add_argument("--port",    type=int, default=DEFAULT_PORT)
    parser.add_argument("--refresh", type=int, default=DEFAULT_REFRESH,
                        help=f"Page refresh interval in seconds (default: {DEFAULT_REFRESH})")
    return parser.parse_args()


def make_handler(refresh_secs: int):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in ("/", "/kanban"):
                self.send_response(404)
                self.end_headers()
                return
            html = generate_html(live_refresh_secs=refresh_secs)
            data = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, fmt, *args):
            pass  # suppress per-request noise

    return Handler


def main():
    args = _parse_args()
    handler = make_handler(args.refresh)
    server = HTTPServer(("localhost", args.port), handler)
    url = f"http://localhost:{args.port}"
    print(f"Kanban live → {url}")
    print(f"Watching: {IDEAS_PATH}")
    print(f"Refreshes every {args.refresh}s · Ctrl+C to stop.\n")
    threading.Timer(0.4, lambda: subprocess.run(["open", url])).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
