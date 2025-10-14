import requests

from typing import Any, Dict
from .data_models import MaestroResponse

# ----------------
# Helper functions
# ----------------

def _safe_json(resp: requests.Response) -> Dict[str, Any]:
    """Try parsing JSON; return empty dict on failure."""
    try:
        return resp.json()
    except Exception:
        return {}

def _wrap_response(resp: requests.Response) -> MaestroResponse:
    """Build a MaestroResponse from a requests.Response."""
    data: Any
    ctype = resp.headers.get("Content-Type", "")
    if "application/json" in ctype:
        data = _safe_json(resp)
    else:
        # If content is text, get .text; else raw bytes
        try:
            if "text/" in ctype:
                data = resp.text
            else:
                data = resp.content
        except Exception:
            data = resp.content

    return MaestroResponse(
        ok=resp.ok,
        status_code=resp.status_code,
        url=str(resp.url),
        headers=dict(resp.headers),
        data=data,
        raw=resp
    )
