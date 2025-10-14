# 🧠 BotCity Maestro API – Python Client

A lightweight, modern, and structured **Python SDK** for interacting with the [BotCity Maestro API (v2)](https://developers.botcity.dev).  
It provides a single entry point, automatic authentication with token caching, and a consistent response interface for all Maestro resources.

---

## 🚀 Features

✅ Token caching and automatic refresh on `401`  
✅ Organized sub-API resources (`tasks`, `bots`, `logs`, `runners`, etc.)  
✅ Consistent `MaestroResponse` object for all HTTP calls  
✅ Low-level `request_raw()` for unwrapped endpoints  
✅ Type hints and full docstrings for IDE auto-completion  

---

## 🧩 Installation

```bash
pip install botcity-maestro-client
```

(Or add the package to your project manually.)

---

## ⚙️ Basic Usage

```python
from maestro_client import MaestroClient

# Instantiate client
client = MaestroClient(
    login="your_login",
    key="your_key",
    base_url="https://developers.botcity.dev"
)

# Authenticate (auto-called if needed)
client.authenticate()

# List tasks
tasks = client.tasks.list(page=1, size=50)
print(tasks.data)

# Get specific task
task = client.tasks.get(task_id="123456")
print(task.data)

# Cancel a task
client.tasks.cancel(task_id="123456")
```

---

## 🧱 Class Overview

### MaestroClient

Main entry point for all BotCity Maestro API interactions.

| Attribute | Type | Description |
|------------|------|-------------|
| `base_url` | `str` | Base URL of the Maestro API (default: `https://developers.botcity.dev`) |
| `login_value` | `str` | User login credential |
| `key_value` | `str` | API key credential |
| `organization` | `str` | Organization label, cached after authentication |
| `token` | `str` | Access token, cached after authentication |

---

### 🔐 Authentication

The client performs authentication via:

```
POST /api/v2/workspace/login
```

Response:
```json
{
  "accessToken": "...",
  "organizationLabel": "ORG123"
}
```

Example:

```python
client.authenticate()
print(client.token)         # Bearer token
print(client.organization)  # Cached organization label
```

The client automatically refreshes the token when it expires or receives `401 Unauthorized`.

---

### 🌐 Making Custom Requests

You can use the low-level helper `request_raw()` to call any API route directly:

```python
response = client.request_raw(
    method="GET",
    path="/api/v2/task",
    params={"size": 50, "page": 0, "sort": "dateCreation"}
)

print(response.status_code)
print(response.data)
```

---

## 🧩 Sub-APIs (Resource Helpers)

Each major Maestro resource is exposed through a dedicated helper, accessible via `client.<resource>`.

| Resource | Endpoint prefix | Description |
|-----------|------------------|-------------|
| `tasks` | `/api/v2/task` | Manage task creation, status, and control |
| `logs` | `/api/v2/log` | Create, list, download, and delete logs |
| `automations` | `/api/v2/activity` | View automations and their metadata |
| `bots` | `/api/v2/bot` | Manage bot versions and repository info |
| `runners` | `/api/v2/machine` | Inspect machine and runner info |
| `credentials` | `/api/v2/credential` | Securely store and retrieve credentials |
| `datapools` | `/api/v2/datapool` | Manage dynamic data pools and their items |
| `result_files` | `/api/v2/artifact` | Handle uploaded and generated artifacts |
| `errors` | `/api/v2/error` | Inspect error logs per automation |
| `schedules` | `/api/v2/scheduling` | Manage and trigger scheduled automations |
| `workspaces` | `/api/v2/workspaces` | Inspect workspace/organization details |

---

## 🧠 Example – Creating a Credential

```python
from botcity_maestro_client import MaestroClient

client = MaestroClient(login="login", key="key")

# Create credential
client.credentials.create(
    label="MyCredential",
    values={
        "user": "user123",
        "password": "pass123"
    }
)
```

**Payload sent:**
```json
{
  "label": "MyCredential",
  "organizationLabel": "ORG123",
  "repositoryLabel": "DEFAULT",
  "secrets": [
    {"key": "user", "value": "user123"},
    {"key": "password", "value": "pass123"}
  ]
}
```

---

## 🧠 Example – Listing Datapools

```python
datapools = client.datapools.list(page=1, size=20)
for dp in datapools.data.get("content", []):
    print(dp["label"], dp["itemCount"])
```

---

## 🔍 MaestroResponse

Every request returns a `MaestroResponse` object with consistent attributes:

| Attribute | Type | Description |
|------------|------|-------------|
| `ok` | `bool` | True if `2xx` response |
| `status_code` | `int` | HTTP status code |
| `url` | `str` | Final request URL |
| `headers` | `dict` | Response headers |
| `data` | `dict` or `bytes` | Parsed JSON or raw content |
| `raw` | `requests.Response` | Original Response object |

Example:

```python
resp = client.tasks.get("12345")
if resp.ok:
    print(resp.data)
else:
    print(f"Error {resp.status_code}: {resp.data}")
```

---

## 🧩 Error Handling

All client-side and HTTP-level errors raise a `MaestroClientError` exception.

```python
from botcity_maestro_client import MaestroClientError

try:
    client.tasks.get("invalid_id")
except MaestroClientError as e:
    print("Error:", e)
```

---

## 🧪 Development

To test locally:

```bash
pip install -r requirements.txt
pytest
```

---

## 📦 Packaging

To publish on PyPI:

```bash
python -m build
twine upload dist/*
```

Package layout suggestion:

```
botcity_maestro_client/
├── __init__.py
├── client.py           # MaestroClient
├── helpers.py          # MaestroResponse, MaestroClientError, etc.
└── ...
```

---

## 🧾 License

MIT License © 2025  
Developed by **Oráculo** 🧠  
Based on the official [BotCity Maestro API v2](https://documentation.botcity.dev/maestro/maestro-api/)

---

## 💬 Support

For API references and examples, see the [official BotCity documentation](https://documentation.botcity.dev/maestro/maestro-api/api-example/).

For SDK issues or contributions, open a GitHub issue or contact the maintainer.
