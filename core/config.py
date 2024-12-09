from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    WEBSOCKET_URL: str
    CHARGE_POINT_ID: str

    model_config = SettingsConfigDict(env_file=".env")


Config = Settings()
