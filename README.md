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

For this below file structure

```bash

> tree
.
├── README.md
├── main.py
├── pyproject.toml
└── uv.lock

```

Import and initialize `watchtower`

```python
from fastapi import FastAPI
from watchtower import setup_watchtower

app = FastAPI(
    title="My Server",
    version="1.0.0",
    description="My ",
)

setup_watchtower(
    app,
    source_root=".",
    code_index_path=".code_index.json",
    output_dir=".server_profile", # <- here you are mentioning where to store the profile logs
    enable_ui=True,
)


@app.get("/")
async def healthcheck():
    return {
        "status": "ok",
    }
```

Then run you server

```bash

uvicorn main:app --reload --port 8000

```

Once the server is up, you can visit this url [http://localhost:8000/__watchtower/](http://localhost:8000/__watchtower/)

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
