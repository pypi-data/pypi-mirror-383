# 🇧🇷 BotCity Maestro Client (pt-BR)

> 📘 Leia esse documento em outros idiomas:  
> 🇺🇸 [English Version](#-botcity-maestro-client-en)

[![PyPI version](https://badge.fury.io/py/botcity-maestro-client.svg)](https://pypi.org/project/botcity-maestro-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**BotCity Maestro Client** é um SDK Python leve e moderno para interação com a [API BotCity Maestro (v2)](https://developers.botcity.dev).  
Ele fornece um ponto de entrada único, autenticação automática com cache de token e uma interface consistente para todas as rotas da API.

---

## 🚀 Instalação

```bash
pip install botcity-maestro-client
```

Dependências:
- [requests](https://requests.readthedocs.io/en/latest/) >= 2.31.0

---

## ⚡ Exemplo rápido

```python
from maestro_client import MaestroClient

# Inicializa o cliente
client = MaestroClient(
    login="seu_login",
    key="sua_chave",
    base_url="https://developers.botcity.dev"
)

# Autentica (executado automaticamente se necessário)
client.authenticate()

# Lista tarefas
tasks = client.tasks.list(page=1, size=50)
print(tasks.data)

# Busca uma tarefa específica
task = client.tasks.get(task_id="123456")
print(task.data)

# Cancela uma tarefa
client.tasks.cancel(task_id="123456")
```

---

## 🧩 Recursos principais

✅ Cache de token e renovação automática em caso de `401 Unauthorized`  
✅ Submódulos organizados (`tasks`, `bots`, `logs`, `runners`, etc.)  
✅ Retorno padronizado via `MaestroResponse`  
✅ Suporte para chamadas diretas com `request_raw()`  
✅ Tipagem completa e docstrings para IDEs  

---

## 🧱 Estrutura da Classe Principal

### `MaestroClient`

Classe principal para interação com a API BotCity Maestro.

| Atributo | Tipo | Descrição |
|-----------|------|-----------|
| `base_url` | `str` | URL base da API Maestro (padrão: `https://developers.botcity.dev`) |
| `login_value` | `str` | Credencial de login |
| `key_value` | `str` | Chave de autenticação |
| `organization` | `str` | Identificador da organização |
| `token` | `str` | Token de acesso com cache automático |

---

### 🔐 Autenticação

A autenticação é realizada via:

```
POST /api/v2/workspace/login
```

Exemplo de uso:

```python
client.authenticate()
print(client.token)         # Bearer token
print(client.organization)  # Organização cacheada
```

---

### 🌐 Requisições personalizadas

Você pode chamar qualquer rota diretamente usando `request_raw()`:

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

## 🧩 Submódulos disponíveis

| Recurso | Endpoint | Descrição |
|----------|-----------|-----------|
| `tasks` | `/api/v2/task` | Gerencia criação, status e controle de tarefas |
| `logs` | `/api/v2/log` | Cria, lista e baixa logs |
| `automations` | `/api/v2/activity` | Lista automações e seus metadados |
| `bots` | `/api/v2/bot` | Gerencia versões e repositórios de bots |
| `runners` | `/api/v2/machine` | Exibe informações sobre máquinas e runners |
| `credentials` | `/api/v2/credential` | Cria e recupera credenciais seguras |
| `datapools` | `/api/v2/datapool` | Gerencia pools de dados e seus itens |
| `result_files` | `/api/v2/artifact` | Manipula arquivos e artefatos de resultado |
| `errors` | `/api/v2/error` | Lista e detalha erros por automação |
| `schedules` | `/api/v2/scheduling` | Cria e gerencia agendamentos |
| `workspaces` | `/api/v2/workspaces` | Consulta informações do workspace |

---

## 💾 Exemplo – Criando uma Credencial

```python
client.credentials.create(
    label="MyCredential",
    values={
        "user": "user123",
        "password": "pass123"
    }
)
```

**Payload enviado:**
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

## 🔍 MaestroResponse

Cada requisição retorna um objeto padronizado `MaestroResponse`.

| Atributo | Tipo | Descrição |
|-----------|------|-----------|
| `ok` | `bool` | Indica se a resposta foi `2xx` |
| `status_code` | `int` | Código HTTP |
| `url` | `str` | URL final requisitada |
| `headers` | `dict` | Cabeçalhos de resposta |
| `data` | `dict` ou `bytes` | Dados decodificados |
| `raw` | `requests.Response` | Objeto original da resposta |

---

## 🧠 Tratamento de erros

Todas as exceções são encapsuladas em `MaestroClientError`.

```python
from maestro_client import MaestroClientError

try:
    client.tasks.get("invalid_id")
except MaestroClientError as e:
    print("Erro:", e)
```

---

## 📂 Estrutura mínima do projeto

```
src/
 └── maestro_client/
      ├── __init__.py
      ├── client.py
      ├── helpers.py
      └── ...
```

---

## 📘 Roadmap
- [ ] Adicionar suporte assíncrono (aiohttp)  
- [ ] Implementar retry com backoff exponencial  
- [ ] Melhorar tipagem de retorno dos submódulos  

---

## 📜 Licença
Distribuído sob a licença MIT.  
© 2025 **Ausier**

---

# 🇺🇸 BotCity Maestro Client (EN)

> 📘 Read this document in other languages:  
> 🇧🇷 [Versão em Português (pt-BR)](#-botcity-maestro-client-pt-br)

[![PyPI version](https://badge.fury.io/py/botcity-maestro-client.svg)](https://pypi.org/project/botcity-maestro-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**BotCity Maestro Client** is a lightweight and modern Python SDK for interacting with the [BotCity Maestro API (v2)](https://developers.botcity.dev).  
It provides a single entry point, automatic token caching, and a unified response structure for all resources.

---

## 🚀 Installation

```bash
pip install botcity-maestro-client
```

Dependencies:
- [requests](https://requests.readthedocs.io/en/latest/) >= 2.31.0

---

## ⚡ Quick Example

```python
from maestro_client import MaestroClient

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
```

---

## 🧱 Class Overview

### `MaestroClient`

Main entry point for all BotCity Maestro API interactions.

| Attribute | Type | Description |
|------------|------|-------------|
| `base_url` | `str` | Base URL of the Maestro API |
| `login_value` | `str` | Login credential |
| `key_value` | `str` | API key credential |
| `organization` | `str` | Cached organization label |
| `token` | `str` | Cached access token |

---

## 🔐 Authentication

Authentication is performed via:

```
POST /api/v2/workspace/login
```

Example:

```python
client.authenticate()
print(client.token)
print(client.organization)
```

The client automatically refreshes tokens when expired or on `401 Unauthorized`.

---

## 🌐 Custom Requests

Use `request_raw()` to call any API route directly:

```python
resp = client.request_raw(
    method="GET",
    path="/api/v2/task",
    params={"page": 1, "size": 20}
)
print(resp.data)
```

---

## 🧩 Submodules

| Resource | Endpoint | Description |
|-----------|-----------|-------------|
| `tasks` | `/api/v2/task` | Manage task creation and control |
| `logs` | `/api/v2/log` | Create and list logs |
| `automations` | `/api/v2/activity` | View automation metadata |
| `bots` | `/api/v2/bot` | Manage bots and versions |
| `runners` | `/api/v2/machine` | Get machine/runner info |
| `credentials` | `/api/v2/credential` | Manage credentials |
| `datapools` | `/api/v2/datapool` | Manage data pools |
| `result_files` | `/api/v2/artifact` | Handle artifacts |
| `errors` | `/api/v2/error` | Inspect automation errors |
| `schedules` | `/api/v2/scheduling` | Manage schedules |
| `workspaces` | `/api/v2/workspaces` | View workspace info |

---

## 🧠 Example – Creating a Credential

```python
client.credentials.create(
    label="MyCredential",
    values={
        "user": "user123",
        "password": "pass123"
    }
)
```

---

## 🧩 Error Handling

All errors raise a `MaestroClientError`.

```python
from maestro_client import MaestroClientError

try:
    client.tasks.get("invalid_id")
except MaestroClientError as e:
    print("Error:", e)
```

---

## 📘 Roadmap
- [ ] Add async support (aiohttp)  
- [ ] Implement exponential retry/backoff  
- [ ] Improve type coverage  

---

## 📜 License
Distributed under the MIT License.  
© 2025 **Ausier**