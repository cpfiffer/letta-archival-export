#!/usr/bin/env python3
"""Export archival memories from a Letta agent.

Usage:
    export.py <agent_id> [--base-url URL] [--output FILE] [--format FORMAT]

Requires:
    pip install letta-client

Set LETTA_API_KEY environment variable or pass --api-key.
"""

import argparse
import json
import os
import sys
import zipfile
from io import BytesIO
from pathlib import Path

try:
    from letta_client import Letta
except ImportError:
    print("Error: letta-client not installed. Run: pip install letta-client", file=sys.stderr)
    sys.exit(1)


def export_passages(client: Letta, agent_id: str, page_size: int = 100) -> list[dict]:
    """Fetch all archival memory passages for an agent using cursor pagination."""
    all_passages = []
    after = None
    page_num = 0

    while True:
        page_num += 1
        kwargs = {"agent_id": agent_id, "limit": page_size, "ascending": True}
        if after:
            kwargs["after"] = after

        page = client.agents.passages.list(**kwargs)
        count = len(page)
        print(f"  Page {page_num}: {count} passages", file=sys.stderr)

        if not page:
            break

        for p in page:
            d = p.model_dump(mode="json")
            # Remove bulky embedding data
            d.pop("embedding", None)
            d.pop("embedding_config", None)
            all_passages.append(d)

        if count < page_size:
            break

        after = page[-1].id

    return all_passages


def write_json(passages: list[dict], output_path: Path) -> None:
    """Write passages as formatted JSON."""
    with open(output_path, "w") as f:
        json.dump(passages, f, indent=2, default=str)
    print(f"Wrote {len(passages)} passages to {output_path}", file=sys.stderr)


def write_zip(passages: list[dict], output_path: Path, agent_id: str) -> None:
    """Write passages as a ZIP containing JSON."""
    json_data = json.dumps(passages, indent=2, default=str)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{agent_id}_memories.json", json_data)
    print(f"Wrote {len(passages)} passages to {output_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Export archival memories from a Letta agent."
    )
    parser.add_argument("agent_id", help="Agent ID (e.g. agent-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)")
    parser.add_argument(
        "--base-url",
        default=None,
        help="Letta server URL (default: https://api.letta.com, or LETTA_BASE_URL env var)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Letta API key (default: LETTA_API_KEY env var)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (default: <agent_id>_memories.json or .zip)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "zip"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=100,
        help="Number of passages per API request (default: 100)",
    )

    args = parser.parse_args()

    api_key = args.api_key or os.getenv("LETTA_API_KEY")
    if not api_key:
        print("Error: No API key. Set LETTA_API_KEY or pass --api-key.", file=sys.stderr)
        sys.exit(1)

    client_kwargs = {"api_key": api_key}
    base_url = args.base_url or os.getenv("LETTA_BASE_URL")
    if base_url:
        client_kwargs["base_url"] = base_url

    client = Letta(**client_kwargs)

    print(f"Exporting archival memories for {args.agent_id}...", file=sys.stderr)
    passages = export_passages(client, args.agent_id, args.page_size)
    print(f"Total: {len(passages)} passages", file=sys.stderr)

    if not passages:
        print("No passages found.", file=sys.stderr)
        sys.exit(0)

    ext = ".zip" if args.format == "zip" else ".json"
    output_path = Path(args.output) if args.output else Path(f"{args.agent_id}_memories{ext}")

    if args.format == "zip":
        write_zip(passages, output_path, args.agent_id)
    else:
        write_json(passages, output_path)


if __name__ == "__main__":
    main()
