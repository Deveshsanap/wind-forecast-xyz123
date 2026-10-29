from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    elexon_api_base_url: str = "https://data.elexon.co.uk/bmrs/api/v1"
    decision_cutoff_time: str = "11:00"

    class Config:
        env_file = ".env"

settings = Settings()