from pydantic import BaseModel


class Settings(BaseModel):
    api_prefix: str = "/api"
    project_name: str = "ml-pipeline-server"
    default_train_split: float = 0.8
    random_seed: int = 42


settings = Settings()
