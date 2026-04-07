from fastapi import FastAPI
from watchtower import WatchTowerMiddleware

from .modules.computation import compute_mean

app = FastAPI()
app.add_middleware(WatchTowerMiddleware, output_dir=".watchtower")


@app.get("/healthcheck")
async def read_root():
    return {"Hello": "World"}


@app.get("/compute/{sample_size}")
async def compute(sample_size: int):
    mean_value = compute_mean(sample_size=sample_size)
    return {"mean": mean_value}