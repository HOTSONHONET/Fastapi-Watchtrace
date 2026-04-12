# WatchTower

WatchTower is a **project-aware FastAPI runtime observability tool** that traces requests across your application and maps them to user-defined classes and functions.

It helps developers:
- understand request flow
- inspect function-level execution
- debug complex pipelines
- visualize backend behavior without framework noise

---

## 🚀 Installation

```bash
pip install fastapi-watchtower
```

or

```bash
uv add fastapi-watchtower
```

---

## ⚙️ Requirements

- Use `async def` endpoints for best tracing accuracy
- Sync endpoints (`def`) may lead to incomplete or unstable traces

---

## 🧪 Example Usage

```python
from fastapi import FastAPI

from .api.routes import router
from .core.config import settings
from .core.logging_util import configure_logging
from watchtower import setup_watchtower

configure_logging()

app = FastAPI(
    title="ML Pipeline Server Example",
    version="1.0.0",
    description="A layered FastAPI example for demonstrating WatchTower tracing on realistic ML pipelines.",
)

setup_watchtower(
    app,
    source_root="examples/ml_pipeline_server",
    code_index_path=".watchtower-ml_pipeline_server/code_index.json",
    output_dir=".watchtower-ml_pipeline_server",
    enable_ui=True,
    ui_dist_dir="frontend/watchtower-ui/dist",
)

app.include_router(router, prefix=settings.api_prefix)

@app.get("/")
async def healthcheck():
    return {
        "status": "ok",
        "service": "ml-pipeline-server",
        "api_prefix": settings.api_prefix,
    }
```

---

## 🎬 Request Flow Visualization

Below is an example of WatchTower tracing a complex FastAPI request flow:

![Request Flow Animation](https://raw.githubusercontent.com/HOTSONHONET/WatchTower/master/assets/request-animation-flow.gif)

---

## ✨ Features

- 🔍 Function-level request tracing
- 🧠 Project-aware filtering (no framework noise)
- 📊 Visual request flow graph
- 🧵 Supports async FastAPI pipelines
- 📦 Zero external dependencies for users (no UI server needed)
- ⚡ Lightweight and easy to integrate

---

## 💡 Why WatchTower?

Modern backend systems are complex:
- nested service calls
- ML pipelines
- async execution flows

Traditional logs don’t show **how execution actually flows**.

WatchTower solves this by giving you:
> **A visual, step-by-step breakdown of what happened inside your backend.**

---

## 🔗 Links

- GitHub: https://github.com/HOTSONHONET/WatchTower
- PyPI: https://pypi.org/project/fastapi-watchtower/

---

## 📄 License

MIT License
