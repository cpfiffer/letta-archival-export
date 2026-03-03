#!/usr/bin/env python3
"""Fix stale archive embedding config by migrating passages to a new archive.

When an agent's embedding model is changed after creation, the existing archive
keeps the old embedding config. This script:
  1. Exports all passages from the old archive
  2. Deletes the old archive
  3. Re-inserts passages (new archive auto-created with agent's current config)

Usage:
    python fix_embedding_config.py <agent_id> [--base-url URL] [--dry-run]

Requires:
    pip install letta-client
"""

import argparse
import json
import os
import sys

try:
    from letta_client import Letta
except ImportError:
    print("Error: letta-client not installed. Run: pip install letta-client", file=sys.stderr)
    sys.exit(1)


def get_all_passages(client, agent_id):
    """Fetch all passages with cursor pagination."""
    passages = []
    after = None
    while True:
        kwargs = {"agent_id": agent_id, "limit": 100, "ascending": True}
        if after:
            kwargs["after"] = after
        page = client.agents.passages.list(**kwargs)
        if not page:
            break
        passages.extend(page)
        if len(page) < 100:
            break
        after = page[-1].id
    return passages


def main():
    parser = argparse.ArgumentParser(
        description="Fix stale archive embedding config by migrating passages."
    )
    parser.add_argument("agent_id", help="Agent ID")
    parser.add_argument("--base-url", default=None, help="Letta server URL (default: localhost:8283)")
    parser.add_argument("--api-key", default=None, help="API key (default: LETTA_API_KEY env var)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without making changes")

    args = parser.parse_args()

    api_key = args.api_key or os.getenv("LETTA_API_KEY")
    base_url = args.base_url or os.getenv("LETTA_BASE_URL", "http://localhost:8283")

    client_kwargs = {"base_url": base_url}
    if api_key:
        client_kwargs["api_key"] = api_key

    client = Letta(**client_kwargs)

    agent_id = args.agent_id

    # Step 1: Get current archives for the agent
    print(f"Checking archives for {agent_id}...", file=sys.stderr)
    archives = client.archives.list(agent_id=agent_id)

    if not archives:
        print("No archives found. Nothing to fix -- next archival memory call will create one with the correct config.", file=sys.stderr)
        sys.exit(0)

    for arc in archives:
        ec = arc.embedding_config
        model = ec.embedding_model if ec else "unknown"
        handle = ec.handle if ec and hasattr(ec, "handle") else "n/a"
        print(f"  Archive {arc.id}: embedding_model={model}, handle={handle}", file=sys.stderr)

    # Step 2: Export all passages
    print(f"Exporting passages...", file=sys.stderr)
    passages = get_all_passages(client, agent_id)
    print(f"  Found {len(passages)} passages", file=sys.stderr)

    # Save backup
    backup_file = f"{agent_id}_passages_backup.json"
    backup_data = []
    for p in passages:
        d = p.model_dump(mode="json")
        d.pop("embedding", None)
        d.pop("embedding_config", None)
        backup_data.append(d)
    with open(backup_file, "w") as f:
        json.dump(backup_data, f, indent=2, default=str)
    print(f"  Backup saved to {backup_file}", file=sys.stderr)

    if args.dry_run:
        print("\n[DRY RUN] Would delete archives and re-insert passages. Run without --dry-run to proceed.", file=sys.stderr)
        sys.exit(0)

    # Step 3: Delete old archives
    for arc in archives:
        print(f"Deleting archive {arc.id}...", file=sys.stderr)
        client.archives.delete(archive_id=arc.id)

    # Step 4: Re-insert passages (first insert triggers new archive creation with current agent config)
    if passages:
        print(f"Re-inserting {len(passages)} passages with new embedding config...", file=sys.stderr)
        for i, p in enumerate(passages):
            client.agents.passages.create(
                agent_id=agent_id,
                text=p.text,
                tags=p.tags if p.tags else None,
            )
            if (i + 1) % 10 == 0:
                print(f"  {i + 1}/{len(passages)}", file=sys.stderr)
        print(f"  Done. All {len(passages)} passages re-inserted.", file=sys.stderr)
    else:
        print("No passages to re-insert. Next archival memory call will create a fresh archive.", file=sys.stderr)

    # Step 5: Verify
    new_archives = client.archives.list(agent_id=agent_id)
    for arc in new_archives:
        ec = arc.embedding_config
        model = ec.embedding_model if ec else "unknown"
        print(f"\nNew archive {arc.id}: embedding_model={model}", file=sys.stderr)

    print("\nDone. Archival memory should now use the agent's current embedding model.", file=sys.stderr)


if __name__ == "__main__":
    main()
