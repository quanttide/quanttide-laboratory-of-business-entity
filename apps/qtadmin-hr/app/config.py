from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./qtcloud-hr.db"
    org_api_url: str = "http://127.0.0.1:8001"
    debug: bool = True

    model_config = {"env_prefix": "QTCLOUD_HR_"}
