# Letta Memory Exporter

A simple Modal web service to export archival memories from Letta agents as compressed JSON archives.

## Features

- Web interface for easy memory export
- Accepts Letta API key and agent ID
- Returns compressed ZIP file containing agent memories
- Deployed on Modal for serverless scaling

## Deployment

1. Install Modal:
```bash
pip install modal
```

2. Authenticate with Modal:
```bash
modal setup
```

3. Deploy the service:
```bash
modal deploy modal_export_service.py
```

Modal will provide a public URL for your service.

## Usage

### Web Interface

1. Navigate to your deployed Modal URL
2. Enter your Letta API key
3. Enter your agent ID (format: `agent-<uuid>`)
4. Click "Export Memories"
5. A ZIP file will download automatically

### API Endpoint

You can also POST directly to the `/export` endpoint:

```bash
curl -X POST https://your-modal-url.modal.run/export \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your-letta-api-key", "agent_id": "agent-xxx"}' \
  --output memories.zip
```

## Output Format

The service exports a ZIP file containing a single JSON file with all archival memories (passages) from the specified agent.

### JSON Structure

The JSON file is an array of passage objects. Each passage contains:

```json
[
  {
    "created_by_id": "user-<uuid>",
    "last_updated_by_id": "user-<uuid>",
    "created_at": "2025-11-05 23:04:24.901468+00:00",
    "updated_at": "2025-11-05 23:04:24.941596+00:00",
    "is_deleted": false,
    "archive_id": "archive-<uuid>",
    "source_id": null,
    "file_id": null,
    "file_name": null,
    "metadata": {},
    "tags": ["production", "bug", "feature"],
    "id": "passage-<uuid>",
    "text": "The actual memory content goes here...",
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

**Note**: The `embedding` and `embedding_config` fields are automatically removed from the export to reduce file size.

## Example Memory

```json
{
  "created_by_id": "user-2bcd6366-fc50-4c5d-9015-b5b3a3e3f988",
  "last_updated_by_id": "user-2bcd6366-fc50-4c5d-9015-b5b3a3e3f988",
  "created_at": "2025-11-06 01:30:07.520938+00:00",
  "updated_at": "2025-11-06 01:30:07.536538+00:00",
  "is_deleted": false,
  "archive_id": "archive-ded47337-40fe-4018-ac9b-82c829f96934",
  "source_id": null,
  "file_id": null,
  "file_name": null,
  "metadata": {},
  "tags": ["breaking-change", "archival-memory", "limits"],
  "id": "passage-5fe757aa-d55b-41c1-9a24-4fe361d83695",
  "text": "Archival Memory Character Limit (Cameron announcement, November 6 2025): New 8k token limit for archival memories. Exceeding this limit will throw an exception requiring users to shrink entries.",
  "organization_id": "org-564296c0-9835-43f2-b79e-c448b26200d4"
}
```

## Requirements

- Letta API key
- Agent ID (must have `agent-` prefix)
- Internet connection

## Error Handling

The service will return error messages for:
- Missing API key or agent ID
- Invalid API credentials
- Agent not found
- API connection issues

Errors are displayed in the web interface or returned as JSON with appropriate HTTP status codes.
