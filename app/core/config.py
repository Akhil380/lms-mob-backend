from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    app_name: str = "LMS-MOCK TEST"
    database_url: str
    sendinblue_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()

