"""
BotCity Maestro API – Python Client

- Base URL: https://developers.botcity.dev
- Single entry point: MaestroClient
- Token caching + auto-refresh on 401
- Consistent response wrapper: MaestroResponse
- Sub-APIs grouped by resource

"""

from __future__ import annotations

import time
import threading
import requests

from typing import Any, Dict, Optional, Union
from .helpers import MaestroClientError, MaestroResponse
from .helpers import _safe_json, _wrap_response


class MaestroClient:
    """
    BotCity Maestro API client with token caching and organized resource helpers.

    Typical usage:
        client = MaestroClient(
            login="your_login",
            key="your_key",
            base_url="https://developers.botcity.dev"
        )

        # Authenticate (auto-called on first request if needed)
        client.authenticate()

        # Use resource helpers
        tasks = client.tasks.list(page=1, size=50)

        # Or make arbitrary calls
        resp = client.request_raw("GET", "/maestro/api/tasks", params={"page": 1, "size": 50})

    Notes:
        - Token & organization are retrieved by POST /maestro/api/login
        - All subsequent requests use Authorization: Bearer <token>
          and the X-Organization (or Organization) header when required by backend.
    """

    def __init__(
        self,
        login: str,
        key: str,
        base_url: str = "https://developers.botcity.dev",
        *,
        request_timeout: float = 30.0,
        token_skew: int = 10,
        default_org_header: str = "X-Organization"
    ):
        """
        Args:
            login: Maestro login credential.
            key: Maestro key credential.
            base_url: Maestro API base URL (no trailing slash required).
            request_timeout: Requests timeout in seconds.
            token_skew: Seconds to subtract from token expiry to avoid race conditions.
            default_org_header: Header name to send the organization value.
        """
        self.base_url = base_url.rstrip("/")
        self.login_value = login
        self.key_value = key
        self.timeout = request_timeout
        self.token_skew = token_skew
        self.org_header_name = default_org_header

        self._token: Optional[str] = None
        self._organization: Optional[str] = None
        self._token_expires_at: float = 0.0
        self._lock = threading.Lock()

        # Resource helpers
        self.tasks = _TasksAPI(self)
        self.logs = _LogsAPI(self)
        self.automations = _AutomationsAPI(self)
        self.bots = _BotsAPI(self)
        self.runners = _RunnersAPI(self)
        self.credentials = _CredentialsAPI(self)
        self.datapools = _DatapoolsAPI(self)
        self.result_files = _ResultFilesAPI(self)
        self.errors = _ErrorsAPI(self)
        self.schedules = _SchedulesAPI(self)
        self.workspaces = _WorkspacesAPI(self)

    # --------
    # Auth
    # --------

    def _is_token_valid(self) -> bool:
        """Return True if we have a token and it hasn't expired considering skew."""
        return bool(self._token) and (time.time() < (self._token_expires_at - self.token_skew))

    def authenticate(self) -> MaestroResponse:
        """
        Perform authentication against Maestro login route and cache token & organization.

        Returns:
            MaestroResponse with token and organization fields.

        Raises:
            MaestroClientError on non-OK responses or malformed payloads.
        """
        url = f"{self.base_url}/api/v2/workspace/login"
        payload = {"login": self.login_value, "key": self.key_value}
        resp = requests.post(url, json=payload, timeout=self.timeout)

        if not resp.ok:
            raise MaestroClientError(f"Authentication failed: {resp.status_code} {resp.text}")

        data = _safe_json(resp)
        token = data.get("accessToken")
        organization = data.get("organizationLabel")

        if not token or not organization:
            raise MaestroClientError(f"Invalid login response. Expected token & organization. Got: {data}")

        with self._lock:
            self._token = token
            self._organization = organization
            self._token_expires_at = time.time() + 3600.0

        return MaestroResponse(
            ok=True,
            status_code=resp.status_code,
            url=url,
            headers=dict(resp.headers),
            data=data,
            raw=resp
        )

    def _auth_headers(self) -> Dict[str, str]:
        """
        Build Authorization headers. Re-auth if token is absent/expired.
        """
        with self._lock:
            if not self._is_token_valid():
                self.authenticate()

            headers = {
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
            }
            # Organization header (required by the API in many calls)
            if self._organization:
                headers[self.org_header_name] = self._organization
            return headers

    # ---------------
    # Core requestor
    # ---------------

    def request_raw(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        retry_on_401: bool = True,
        stream: bool = False,
    ) -> MaestroResponse:
        """
        Low-level request method. Use this to call any route not yet wrapped.

        Args:
            method: HTTP verb (GET/POST/PUT/DELETE/PATCH).
            path: Absolute path or relative to base (e.g., "/maestro/api/tasks").
            params: Querystring parameters.
            json: JSON body.
            files: Files dict for multipart/form-data.
            headers: Additional headers (merged with auth headers).
            retry_on_401: If True, on 401 the client will re-auth and retry once.
            stream: If True, return the Response with streaming content.

        Returns:
            MaestroResponse
        """
        url = self._normalize_url(path)
        base_headers = self._auth_headers()
        if headers:
            base_headers.update(headers)

        resp = requests.request(
            method=method.upper(),
            url=url,
            headers=base_headers,
            params=params,
            json=json if files is None else None,
            files=files,
            timeout=self.timeout,
            stream=stream
        )

        # If unauthorized, try to refresh token once and retry.
        if resp.status_code == 401 and retry_on_401:
            with self._lock:
                # Force a new token
                self.authenticate()
            base_headers = self._auth_headers()
            if headers:
                base_headers.update(headers)
            resp = requests.request(
                method=method.upper(),
                url=url,
                headers=base_headers,
                params=params,
                json=json if files is None else None,
                files=files,
                timeout=self.timeout,
                stream=stream
            )

        return _wrap_response(resp)

    def _normalize_url(self, path: str) -> str:
        """
        Ensure a valid absolute URL:
        - If 'path' already starts with http, return as-is.
        - Else, resolve relative to <base_url>.
          If it doesn't start with '/maestro/api', we prepend it.
        """
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        if not path.startswith("/api/v2"):
            path = "/api/v2" + path
        return f"{self.base_url}{path}"

    # -------------
    # Utilities
    # -------------

    @property
    def token(self) -> Optional[str]:
        """Return the cached token (if any)."""
        return self._token

    @property
    def organization(self) -> Optional[str]:
        """Return the cached organization (if any)."""
        return self._organization

    def set_organization(self, organization: str) -> None:
        """
        Manually override the cached organization header value.

        Useful in multi-workspace contexts if your login returns multiple orgs
        or you need to switch org context without re-authenticating.
        """
        with self._lock:
            self._organization = organization


# ------------------------
# Resource Helper Classes
# ------------------------

class _TasksAPI:
    """
    Tasks-related routes.
    Common patterns observed in Maestro CLI & docs:
      - GET /tasks
      - POST /tasks
      - GET /tasks/{taskId}
      - POST /tasks/{taskId}/cancel
      - POST /tasks/{taskId}/finish
      - POST /tasks/{taskId}/restart
    """

    def __init__(self, client: MaestroClient):
        self._c = client

    def list(self, **kwargs) -> MaestroResponse:
        """GET /tasks"""
        query_params = "&".join(f"{k}={v}" for k, v in kwargs.items() if v is not None)
        return self._c.request_raw("GET", f"/api/v2/task?{query_params}")

    def create(self, automation_label: str, data: Dict[str, Any]) -> MaestroResponse:
        """POST /tasks"""
        payload = {"automationLabel": automation_label, "data": data}
        return self._c.request_raw("POST", "/api/v2/task", json=payload)

    def get(self, task_id: Union[str, int]) -> MaestroResponse:
        """GET /tasks/{taskId}"""
        return self._c.request_raw("GET", f"/api/v2/task/{task_id}")

    def cancel(self, task_id: Union[str, int]) -> MaestroResponse:
        """POST /tasks/{taskId}/cancel"""
        return self._c.request_raw("POST", f"/api/v2/task/{task_id}/cancel")

    def finish(self, task_id: Union[str, int], result: Optional[Dict[str, Any]] = None) -> MaestroResponse:
        """POST /tasks/{taskId}/finish"""
        return self._c.request_raw("POST", f"/api/v2/task/{task_id}/finish", json=result or {})

    def restart(self, task_id: Union[str, int]) -> MaestroResponse:
        """POST /tasks/{taskId}/restart"""
        return self._c.request_raw("POST", f"/api/v2/task/{task_id}/restart")


class _LogsAPI:
    """
    Logs-related routes.
      - POST /logs
      - GET /logs?...
      - GET /logs/{logId}
      - DELETE /logs/{logId}
      - GET /logs/{logId}/download
    """

    def __init__(self, client: MaestroClient):
        self._c = client

    def create(self, label: str, message: str, level: str = "INFO", **kwargs) -> MaestroResponse:
        """POST /logs"""
        payload = {"label": label, "message": message, "level": level}
        payload.update(kwargs)
        return self._c.request_raw("POST", "/maestro/api/logs", json=payload)

    def list(self, *, label: Optional[str] = None, page: int = 1, size: int = 50,
             extra: Optional[Dict[str, Any]] = None) -> MaestroResponse:
        """GET /logs"""
        params = {"page": page, "size": size}
        if label:
            params["label"] = label
        if extra:
            params.update(extra)
        return self._c.request_raw("GET", "/maestro/api/logs", params=params)

    def get(self, log_id: Union[str, int]) -> MaestroResponse:
        """GET /logs/{logId}"""
        return self._c.request_raw("GET", f"/maestro/api/logs/{log_id}")

    def delete(self, log_id: Union[str, int]) -> MaestroResponse:
        """DELETE /logs/{logId}"""
        return self._c.request_raw("DELETE", f"/maestro/api/logs/{log_id}")

    def download(self, log_id: Union[str, int]) -> MaestroResponse:
        """GET /logs/{logId}/download"""
        # stream not necessary unless huge; keeping simple.
        return self._c.request_raw("GET", f"/maestro/api/logs/{log_id}/download")


class _AutomationsAPI:
    """
    Automations-related routes.
      - GET /automations
      - GET /automations/{id}
      - (Sometimes create/update via bots upload or CI/CD – kept generic)
    """

    def __init__(self, client: MaestroClient):
        self._c = client

    def list(self, *, label: Optional[str] = None, page: int = 1, size: int = 50,
             extra: Optional[Dict[str, Any]] = None) -> MaestroResponse:
        """GET /automations"""
        params = {"page": page, "size": size}
        if label:
            params["label"] = label
        if extra:
            params.update(extra)
        return self._c.request_raw("GET", "/api/v2/activity", params=params)

    def get(self, automation_label:str) -> MaestroResponse:
        """GET /automations/{id}"""
        return self._c.request_raw("GET", f"/api/v2/activity/{automation_label}")


class _BotsAPI:
    """
    Bots-related routes.
      - GET /bots
      - GET /bots/{botId}
      - POST /bots
      - PUT /bots/{botId}
      - Optional routes: /bots/{botId}/release etc., depending on workspace features
    """

    def __init__(self, client: MaestroClient):
        self._c = client

    def list(self, page: int = 1, size: int = 50, extra: Optional[Dict[str, Any]] = None) -> MaestroResponse:
        """GET /bots"""
        params = {"page": page, "size": size}
        if extra:
            params.update(extra)
        return self._c.request_raw("GET", "/api/v2/bot", params=params)

    def get(self, bot_id:str, bot_version:str) -> MaestroResponse:
        """GET /bots/{botId}"""
        return self._c.request_raw("GET", f"/api/v2/bot/{bot_id}/version/{bot_version}")

    def create(self, *, label: str, repository: Optional[str] = None, **kwargs) -> MaestroResponse:
        """POST /bots"""
        payload = {"label": label}
        if repository:
            payload["repository"] = repository
        payload.update(kwargs)
        return self._c.request_raw("POST", "/api/v2/bot", json=payload)

    def update(self, bot_id: Union[str, int], **fields) -> MaestroResponse:
        """PUT /bots/{botId}"""
        return self._c.request_raw("PUT", f"/api/v2/bot/{bot_id}", json=fields)

    def release(self, bot_id: Union[str, int], **fields) -> MaestroResponse:
        """POST /bots/{botId}/release (if supported)"""
        return self._c.request_raw("POST", f"/api/v2/bot/{bot_id}/release", json=fields)


class _RunnersAPI:
    """
    Runners-related routes.
      - GET /runners
      - GET /runners/{runnerId}
      - (actions may exist such as attach/release via Session Manager; keep generic endpoints)
    """

    def __init__(self, client: MaestroClient):
        self._c = client

    def get_info(self, runner_id: Union[str, int]) -> MaestroResponse:
        """GET /runners/{runnerId}"""
        return self._c.request_raw("GET", f"/api/v2/machine/{runner_id}")

    def get_log(self, runner_id: Union[str, int]) -> MaestroResponse:
        """GET /runners/{runnerId}"""
        return self._c.request_raw("GET", f"/api/v2/machine/log/{runner_id}")
    
    def get_tasks_summary(self, runner_id: Union[str, int]) -> MaestroResponse:
        """GET /runners/{runnerId}"""
        return self._c.request_raw("GET", f"/api/v2/machine/{runner_id}/tasks-summary?days=30")
    

class _CredentialsAPI:
    """
    Credentials-related routes.
      - GET /credentials
      - GET /credentials/{id}
      - POST /credentials
      - PUT /credentials/{id}
      - DELETE /credentials/{id}
      - GET /credentials/{label}/{key}  (common pattern for key retrieval)
    """

    def __init__(self, client: MaestroClient):
        self._c = client

    def list(self, page: int = 1, size: int = 50, extra: Optional[Dict[str, Any]] = None) -> MaestroResponse:
        """GET /credentials"""
        params = {"page": page, "size": size}
        if extra:
            params.update(extra)
        return self._c.request_raw("GET", "/api/v2/credential", params=params)

    def get(self, credential_id: Union[str, int]) -> MaestroResponse:
        """GET /credentials/{id}"""
        return self._c.request_raw("GET", f"/api/v2/credential/{credential_id}")

    def get_key(self, credential_id:str, credential_key:str) -> MaestroResponse:
        """GET /credentials/{id}"""
        return self._c.request_raw("GET", f"/api/v2/credential/{credential_id}/key/{credential_key}")
    
    def create(self, label:str, values:Dict[str, Any], repository_label:str="DEFAULT", **kwargs) -> MaestroResponse:
        """
        Create a new credential entry in BotCity Maestro.

        Args:
            label: Credential label name.
            values: Dict with secret key-value pairs
            repository_label: Credential repository label (defaults to DEFAULT).
        """
        secrets = [{"key": k, "value": v} for k, v in values.items()]
        payload = {
            "label": label,
            "organizationLabel": self._c.organization,
            "repositoryLabel": repository_label,
            "secrets": secrets
        }
        payload.update(kwargs)
        return self._c.request_raw("POST", "/api/v2/credential", json=payload)


class _DatapoolsAPI:
    """
    Datapool-related routes.
      - GET /datapools
      - GET /datapools/{label}/items
      - POST /datapools/{label}/items
      - PUT /datapools/{label}/items/{itemId}
      - DELETE /datapools/{label}/items/{itemId}
    """

    def __init__(self, client: MaestroClient):
        self._c = client

    def list(self, page: int = 1, size: int = 50, extra: Optional[Dict[str, Any]] = None) -> MaestroResponse:
        """GET /datapools"""
        params = {"page": page, "size": size}
        if extra:
            params.update(extra)
        return self._c.request_raw("GET", "/api/v2/datapool", params=params)
    
    def get(self, datapool_label:str) -> MaestroResponse:
        return self._c.request_raw("GET", f"/api/v2/datapool/{datapool_label}")

    def view(self, datapool_label:str) -> MaestroResponse:
        return self._c.request_raw("GET", f"/api/v2/datapool/{datapool_label}/view")
    
    def summary(self, datapool_label:str) -> MaestroResponse:
        return self._c.request_raw("GET", f"/api/v2/datapool/{datapool_label}/summary")
    
    def create(self, **kwargs) -> MaestroResponse:
        return self._c.request_raw("POST", f"/api/v2/datapool", json=kwargs)
    
    def add_item(self, datapool_label:str, **kwargs) -> MaestroResponse:
        return self._c.request_raw("POST", f"/api/v2/datapool/{datapool_label}/push", json=kwargs)


class _ResultFilesAPI:
    """
    Result Files-related routes.
      - GET /artifacts
      - GET /artifacts/{artifactId}
      - GET /artifacts/{artifactId}/download
      - POST /artifacts (multipart/form-data)
      - DELETE /artifacts/{artifactId}
    """

    def __init__(self, client: MaestroClient):
        self._c = client

    def list(self, page: int = 1, size: int = 50, **kwargs) -> MaestroResponse:
        """GET /artifacts"""
        kwargs_query_string = ""
        if kwargs:
            kwargs_query_string = "&" + "&".join(f"{k}={v}" for k, v in kwargs.items() if v is not None)

        return self._c.request_raw("GET", f"/api/v2/artifact?size={size}&page={page}{kwargs_query_string}")

    def get(self, artifact_id: Union[str, int]) -> MaestroResponse:
        """GET /artifacts/{artifactId}"""
        return self._c.request_raw("GET", f"/api/v2/artifact/{artifact_id}")

    def get_file(self, artifact_id: Union[str, int]) -> MaestroResponse:
        """GET /artifacts/{artifactId}/download"""
        return self._c.request_raw("GET", f"/api/v2/artifact/{artifact_id}/file")


class _ErrorsAPI:
    """
    Errors-related routes.
      - GET /errors
      - GET /errors/{errorId}
      - DELETE /errors/{errorId}
    """

    def __init__(self, client: MaestroClient):
        self._c = client

    def list(self, page: int = 1, size: int = 50, extra: Optional[Dict[str, Any]] = None) -> MaestroResponse:
        """GET /errors"""
        params = {"page": page, "size": size}
        if extra:
            params.update(extra)
        return self._c.request_raw("GET", "/api/v2/error", params=params)

    def get(self, error_id: Union[str, int]) -> MaestroResponse:
        """GET /errors/{errorId}"""
        return self._c.request_raw("GET", f"/api/v2/error/{error_id}")

    def get_by_automation(self, automation_label:str) -> MaestroResponse:
        return self._c.request_raw("GET", f"/api/v2/error?AutomationLabel={automation_label}&days=30")


class _SchedulesAPI:
    """
    Schedules-related routes.
      - GET /schedules
      - GET /schedules/{id}
      - POST /schedules
      - PUT /schedules/{id}
      - DELETE /schedules/{id}
    """

    def __init__(self, client: MaestroClient):
        self._c = client

    def list(self, page: int = 1, size: int = 50, extra: Optional[Dict[str, Any]] = None) -> MaestroResponse:
        """GET /schedules"""
        params = {"page": page, "size": size}
        if extra:
            params.update(extra)
        return self._c.request_raw("GET", "/api/v2/scheduling", params=params)

    def get(self, schedule_id: Union[str, int]) -> MaestroResponse:
        """GET /schedules/{id}"""
        return self._c.request_raw("GET", f"/api/v2/scheduling/{schedule_id}")

    def create(self, **fields) -> MaestroResponse:
        """POST /schedules"""
        return self._c.request_raw("POST", "/api/v2/scheduling", json=fields)

    def update(self, schedule_id: Union[str, int], **fields) -> MaestroResponse:
        """PUT /schedules/{id}"""
        return self._c.request_raw("PUT", f"/api/v2/scheduling/{schedule_id}", json=fields)

    def delete(self, schedule_id: Union[str, int]) -> MaestroResponse:
        """DELETE /schedules/{id}"""
        return self._c.request_raw("DELETE", f"/api/v2/scheduling/{schedule_id}")


class _WorkspacesAPI:
    """
    Workspaces/Organization routes (read-only in most public cases).
      - GET /workspaces
      - GET /workspaces/{id}
    """

    def __init__(self, client: MaestroClient):
        self._c = client

    def list(self, page: int = 1, size: int = 50, extra: Optional[Dict[str, Any]] = None) -> MaestroResponse:
        """GET /workspaces"""
        params = {"page": page, "size": size}
        if extra:
            params.update(extra)
        return self._c.request_raw("GET", "/maestro/api/workspaces", params=params)

    def get(self, workspace_id: Union[str, int]) -> MaestroResponse:
        """GET /workspaces/{id}"""
        return self._c.request_raw("GET", f"/maestro/api/workspaces/{workspace_id}")



