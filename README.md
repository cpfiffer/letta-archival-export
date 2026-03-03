# Letta Memory Exporter

Export archival memories from Letta agents as JSON or ZIP.

## Python CLI (Recommended)

Uses the official `letta-client` SDK with cursor pagination.

### Install

```bash
pip install letta-client
```

### Usage

```bash
# Set your API key
export LETTA_API_KEY=sk-...

# Export as JSON (default)
python export.py agent-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Export as ZIP
python export.py agent-xxx -f zip

# Custom output path
python export.py agent-xxx -o my-export.json

# Self-hosted server
python export.py agent-xxx --base-url http://localhost:8283
```

### Options

```
positional arguments:
  agent_id              Agent ID (agent-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)

options:
  --base-url URL        Letta server URL (default: https://api.letta.com)
  --api-key KEY         API key (default: LETTA_API_KEY env var)
  --output, -o FILE     Output file path
  --format, -f FORMAT   json or zip (default: json)
  --page-size N         Passages per request (default: 100)
```

## Web Interface

A client-side HTML page that exports directly from your browser.

### Online

Visit: [https://cpfiffer.github.io/letta-archival-export](https://cpfiffer.github.io/letta-archival-export)

### Local

1. Open `index.html` in your browser
2. Enter your Letta API key and agent ID
3. Click "Export Memories"

## Output Format

Both tools export a JSON array of passage objects with `embedding` and `embedding_config` fields removed:

```json
[
  {
    "text": "The actual memory content...",
    "id": "passage-<uuid>",
    "archive_id": "archive-<uuid>",
    "created_at": "2025-11-05T23:04:24.901468Z",
    "updated_at": "2025-11-05T23:04:24.941596Z",
    "is_deleted": false,
    "metadata": {},
    "tags": ["production", "bug", "feature"],
    "created_by_id": "user-<uuid>",
    "last_updated_by_id": "user-<uuid>",
    "source_id": null,
    "file_id": null,
    "file_name": null,
    "organization_id": "org-<uuid>"
  }
]
```

### Field Descriptions

- `id`: Unique passage identifier
- `text`: The actual memory content
- `tags`: Array of tags for categorization
- `created_at` / `updated_at`: Timestamps
- `archive_id`: Parent archive identifier
- `source_id` / `file_id`: Optional source references
- `metadata`: Custom metadata object
- `organization_id`: Organization identifier
- `is_deleted`: Soft delete flag

## Privacy & Security

- Python CLI: API key stays local
- Web interface: API calls go directly from browser to Letta API, key never sent to third parties

## License

MIT License - see [LICENSE](LICENSE) file for details
