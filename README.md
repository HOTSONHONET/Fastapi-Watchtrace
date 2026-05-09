# WatchTrace

WatchTrace is a **project-aware FastAPI runtime observability tool** that traces requests across your application and maps them to user-defined classes and functions.

It helps developers:
- understand request flow
- inspect function-level execution
- debug complex pipelines
- visualize backend behavior without framework noise

---

## 🚀 Installation

```bash
pip install fastapi-watchtrace
```

or

```bash
uv add fastapi-watchtrace
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

Import and initialize `watchtrace`

```python
from fastapi import FastAPI
from watchtrace import setup_watchtrace

app = FastAPI(
    title="My Server",
    version="1.0.0",
    description="My Server",
)

setup_watchtrace(
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

Once the server is up, you can visit this url [http://localhost:8000/__watchtrace/](http://localhost:8000/__watchtrace/)

---

## 🎬 Request Flow Visualization

Below is an example of WatchTrace tracing a complex FastAPI request flow:

![Request Flow Animation](https://raw.githubusercontent.com/HOTSONHONET/Fastapi-Watchtrace/refs/heads/master/assets/request-animation-flow.gif)

---

## ✨ Features

- 🔍 Function-level request tracing
- 🧠 Project-aware filtering (no framework noise)
- 📊 Visual request flow graph
- 🧵 Supports async FastAPI pipelines
- 📦 Zero external dependencies for users (no UI server needed)
- ⚡ Lightweight and easy to integrate

---

## 💡 Why WatchTrace?

Modern backend systems are complex:
- nested service calls
- ML pipelines
- async execution flows

Traditional logs don’t show **how execution actually flows**.

WatchTrace solves this by giving you:
> **A visual, step-by-step breakdown of what happened inside your backend.**

---

---

## 🛠️ Local Development

Clone the repository:

```bash
git clone https://github.com/HOTSONHONET/WatchTrace.git
cd WatchTrace
```

Install dependencies using `uv`:

```bash
uv sync
```

Run the frontend in development mode:

```bash
cd frontend/watchtrace-ui
npm install
npm run dev
```

Build the frontend UI:

```bash
npm run build
```

The generated UI assets will be available inside:

```bash
frontend/watchtrace-ui/dist
```

Run the example ML pipeline server:

```bash
uv run uvicorn examples.ml_pipeline_server.main:app --reload
```

Open WatchTrace UI:

```text
http://localhost:8000/__watchtrace/
```

---

## ✅ Testing

Run all unit tests:

```bash
uv run --with pytest pytest tests/unit_test
```

Build the package locally:

```bash
uv build
```

Validate package metadata:

```bash
uv run --with twine twine check dist/*
```

Run wheel smoke test:

```bash
./scripts/smoke_test_wheel.sh
```

The smoke test validates:
- packaged wheel installation
- WatchTrace UI mounting
- internal API availability
- generated frontend asset serving

---

## 📦 Releasing a New Version

Update the version inside `pyproject.toml`:

```toml
version = "0.0.1"
```

Build the package:

```bash
rm -rf dist build src/*.egg-info
uv build
```

Validate the package:

```bash
uv run --with twine twine check dist/*
```

Upload manually to PyPI:

```bash
uv run --with twine twine upload dist/*
```

Or create a release tag for CI/CD publishing:

```bash
git tag v0.0.1
git push origin v0.0.1
```

WatchTrace uses semantic versioning:

```text
MAJOR.MINOR.PATCH
```

Examples:
- `0.1.0` → new feature
- `0.1.1` → bug fix
- `1.0.0` → stable public release

---


## 🔗 Links

- GitHub: https://github.com/HOTSONHONET/WatchTrace
- PyPI: https://pypi.org/project/fastapi-watchtrace/

---

## 📄 License

MIT License
