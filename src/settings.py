# Third party imports
import os
from logging import getLogger

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = getLogger()


class Settings(BaseSettings):
    """
    Configuration settings for the application.
    """

    host: str = os.getenv("HOST")
    port: int = os.getenv("PORT")
    reload: bool = os.getenv("RELOAD")
    debug: bool = None
    database_url: str = None
    api_key: str = None
    new_api_key: str = None
    possible_date_formats: set = frozenset(
        {"%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d %I:%M %p", "%Y-%m-%d", "%I:%M %p", "%H:%M"}
    )

    model_config = SettingsConfigDict(env_file=".env", extra="allow", populate_by_name=True, validate_assignment=False)


class DevSettings(Settings):
    """
    Development environment settings.
    """

    debug: bool = True
    database_url: str = "sqlite:///:memory:"


class TestSettings(Settings):
    """
    Test environment settings.
    """

    debug: bool = False
    database_url: str = "sqlite:///:memory:"


class ProdSettings(Settings):
    """
    Production environment settings.
    """

    debug: bool = False
    database_url: str = "postgresql+psycopg2://postgres:aircraftdb@localhost:5433/postgres"
    api_key: str = os.getenv("API_KEY")
    new_api_key: str = os.getenv("NEW_API_KEY")


def load_settings() -> Settings:
    """
    Loads the appropriate settings based on the environment.

    Returns
    -------
    Settings
        An instance of the appropriate settings class.
    """
    env = os.getenv("ENV", "dev")
    logger.info(env)
    print(env)
    if env == "prod":
        return ProdSettings()
    elif env == "test":
        return TestSettings()
    else:
        return DevSettings()
