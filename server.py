#!/usr/bin/env python3
"""Local server for the Letta Memory Exporter web UI.

Serves index.html and proxies API calls to avoid browser CORS restrictions.

Usage:
    python server.py [--port 8080]

Requires:
    pip install letta-client
"""

import argparse
import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

try:
    from letta_client import Letta
except ImportError:
    print("Error: letta-client not installed. Run: pip install letta-client", file=sys.stderr)
    sys.exit(1)


class ExportHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/export":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))

        api_key = body.get("api_key", "")
        agent_id = body.get("agent_id", "")
        base_url = body.get("base_url", "https://api.letta.com")

        if not api_key or not agent_id:
            self._json_response(400, {"error": "api_key and agent_id required"})
            return

        try:
            client = Letta(api_key=api_key, base_url=base_url)
            passages = []
            after = None

            while True:
                kwargs = {"agent_id": agent_id, "limit": 100, "ascending": True}
                if after:
                    kwargs["after"] = after
                page = client.agents.passages.list(**kwargs)
                if not page:
                    break
                for p in page:
                    d = p.model_dump(mode="json")
                    d.pop("embedding", None)
                    d.pop("embedding_config", None)
                    passages.append(d)
                if len(page) < 100:
                    break
                after = page[-1].id

            self._json_response(200, {"passages": passages, "count": len(passages)})

        except Exception as e:
            self._json_response(500, {"error": str(e)})

    def _json_response(self, code, data):
        body = json.dumps(data, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Quieter logging
        if "/export" in str(args):
            sys.stderr.write(f"[export] {args[0]}\n")


def main():
    parser = argparse.ArgumentParser(description="Letta Memory Exporter web UI")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(("127.0.0.1", args.port), ExportHandler)
    print(f"Open http://localhost:{args.port} in your browser")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
