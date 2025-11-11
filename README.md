# Letta Memory Exporter

A simple static web page to export archival memories from Letta agents as compressed ZIP archives.

## Features

- Pure client-side, no server required
- Secure: API key never leaves your browser
- Web interface for easy memory export
- ZIP compression for universal compatibility
- Can be hosted on GitHub Pages or any static host

## Usage

### Online

Visit the hosted version: [https://cpfiffer.github.io/letta-archival-export](https://cpfiffer.github.io/letta-archival-export)

### Local

1. Download `index.html`
2. Open it in your browser
3. Enter your Letta API key, base URL (optional), and agent ID
4. Click "Export Memories"
5. A ZIP file will download automatically

## Hosting Your Own

### GitHub Pages

1. Fork this repository
2. Go to Settings → Pages
3. Set source to "main branch"
4. Your page will be available at `https://yourusername.github.io/letta-archival-export`

### Other Static Hosts

Upload `index.html` to any static hosting service:
- Netlify
- Vercel
- Cloudflare Pages
- Amazon S3
- Or just open the file locally

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

- Modern web browser with JavaScript enabled
- Letta API key
- Agent ID (must have `agent-` prefix)
- Internet connection (for CDN resources)

## Privacy & Security

- All API calls are made directly from your browser to Letta's API
- Your API key is never sent to any third-party server
- No data is collected or stored by this tool
- Everything runs client-side in your browser

## Error Handling

The tool will display error messages for:
- Missing API key or agent ID
- Invalid API credentials
- Agent not found
- API connection issues
- Network errors

## Technical Details

- Uses [JSZip](https://stoutner.com/jszip/) for client-side ZIP compression
- Pure JavaScript, no build process required
- Compatible with all modern browsers
- Works offline after initial load (CDN resources cached)

## License

MIT License - see [LICENSE](LICENSE) file for details
