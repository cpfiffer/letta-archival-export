import io
import json
import zipfile
from typing import Any, Dict, List

import modal
from letta_client import Letta

app = modal.App("letta-memory-exporter")
image = modal.Image.debian_slim().pip_install("letta-client", "fastapi[standard]")


def export_agent_memories(
    client: Letta,
    agent_id: str,
    page_limit: int = 100,
) -> List[Dict[str, Any]]:
    all_passages = []
    after_cursor = None

    while True:
        try:
            passages = client.agents.passages.list(
                agent_id=agent_id,
                after=after_cursor,
                limit=page_limit,
                ascending=True,
            )
        except Exception as e:
            raise Exception(f"Error fetching memories: {e}")

        if not passages:
            break

        for passage in passages:
            passage_dict = (
                passage.model_dump()
                if hasattr(passage, "model_dump")
                else passage.dict()
            )
            passage_dict.pop("embedding", None)
            passage_dict.pop("embedding_config", None)
            all_passages.append(passage_dict)

        if len(passages) < page_limit:
            break

        after_cursor = (
            passages[-1].id if hasattr(passages[-1], "id") else passages[-1]["id"]
        )

    return all_passages


@app.function(image=image)
@modal.asgi_app()
def fastapi_app():
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, Response

    web_app = FastAPI()

    @web_app.get("/")
    def index():
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Letta Memory Exporter</title>
            <style>
                body { font-family: system-ui; max-width: 600px; margin: 50px auto; padding: 20px; }
                input { width: 100%; padding: 8px; margin: 8px 0; box-sizing: border-box; }
                button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
                button:hover { background: #0056b3; }
                .status { margin-top: 20px; padding: 10px; }
                .error { background: #fee; color: #c00; }
                .success { background: #efe; color: #060; }
            </style>
        </head>
        <body>
            <h1>Letta Memory Exporter</h1>
            <form id="exportForm">
                <label>API Key:</label>
                <input type="password" id="apiKey" required>
                <label>Agent ID:</label>
                <input type="text" id="agentId" required>
                <button type="submit">Export Memories</button>
            </form>
            <div id="status"></div>
            <script>
                document.getElementById('exportForm').onsubmit = async (e) => {
                    e.preventDefault();
                    const status = document.getElementById('status');
                    status.innerHTML = 'Exporting...';
                    status.className = 'status';
                    
                    try {
                        const response = await fetch('/export', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                api_key: document.getElementById('apiKey').value,
                                agent_id: document.getElementById('agentId').value
                            })
                        });
                        
                        if (response.ok) {
                            const blob = await response.blob();
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = response.headers.get('Content-Disposition').match(/filename=(.+)/)[1];
                            a.click();
                            status.innerHTML = 'Export successful!';
                            status.className = 'status success';
                        } else {
                            const error = await response.json();
                            status.innerHTML = 'Error: ' + error.error;
                            status.className = 'status error';
                        }
                    } catch (err) {
                        status.innerHTML = 'Error: ' + err.message;
                        status.className = 'status error';
                    }
                };
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

    @web_app.post("/export")
    def export(data: Dict[str, str]):
        api_key = data.get("api_key")
        agent_id = data.get("agent_id")

        if not api_key or not agent_id:
            return {"error": "api_key and agent_id are required"}, 400

        try:
            client = Letta(token=api_key)
            passages = export_agent_memories(client=client, agent_id=agent_id)

            json_data = json.dumps(passages, default=str)
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(f"{agent_id}_memories.json", json_data)
            
            return Response(
                content=zip_buffer.getvalue(),
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename={agent_id}_memories.zip",
                },
            )

        except Exception as e:
            return {"error": str(e)}, 500

    return web_app
