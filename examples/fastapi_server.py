from fastapi import FastAPI
from watchtower import WatchTowerMiddleware, setup_watchtower
from fastapi.middleware.cors import CORSMiddleware

from .modules.computation import compute_mean

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_watchtower(
    app,
    source_root="examples",
    output_dir=".watchtower",
)

@app.get("/healthcheck")
async def read_root():
    return {"Hello": "World"}


@app.get("/compute/{sample_size}")
async def compute(sample_size: int):
    mean_value = compute_mean(sample_size=sample_size)
    return {"mean": mean_value}