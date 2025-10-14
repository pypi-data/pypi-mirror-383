from __future__ import annotations

import requests

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class MaestroResponse:
    """
    Standardized response wrapper for Maestro API calls.

    Attributes:
        ok: True if HTTP status is in 2xx.
        status_code: HTTP status code.
        url: Final URL that was called.
        headers: Response headers.
        data: Parsed JSON (dict/list) when possible; else raw bytes/text.
        raw: The original requests.Response object (optional for deep inspection).
    """
    ok: bool
    status_code: int
    url: str
    headers: Dict[str, str]
    data: Any
    raw: Optional[requests.Response] = None
