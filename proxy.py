"""Modal CORS proxy for Letta Memory Exporter.

Deploys a single /export endpoint that the GitHub Pages HTML calls.
The Python SDK handles pagination server-side -- no CORS issues.

Deploy:
    modal deploy proxy.py

The endpoint URL will be printed after deploy. Update PROXY_URL in index.html.
"""

import modal

app = modal.App("letta-archival-export")
image = modal.Image.debian_slim().pip_install("letta-client", "fastapi[standard]")


@app.function(image=image)
@modal.asgi_app()
def web():
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from typing import Optional

    api = FastAPI()

    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class ExportRequest(BaseModel):
        api_key: str
        agent_id: str
        base_url: Optional[str] = "https://api.letta.com"

    @api.post("/export")
    def export(req: ExportRequest):
        from letta_client import Letta

        client_kwargs = {"api_key": req.api_key}
        if req.base_url:
            client_kwargs["base_url"] = req.base_url

        client = Letta(**client_kwargs)

        passages = []
        after = None
        while True:
            kwargs = {"agent_id": req.agent_id, "limit": 100, "ascending": True}
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

        return {"passages": passages, "count": len(passages)}

    @api.get("/health")
    def health():
        return {"ok": True}

    return api
