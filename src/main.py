# Third party imports
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings

# Internal imports
from src.config.database import engine
from src.exceptions import DatabaseConnectionError
from src.router.api import router as router_aircraft
from src.utils.init_db import create_tables

load_dotenv(".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseConfig(BaseSettings):
    host: str = os.getenv("HOST")
    port: int = os.getenv("PORT")
    reload: bool = os.getenv("RELOAD")


@asynccontextmanager
async def lifespan(fastapp: FastAPI):
    try:
        logger.info("Creating database tables...")
        create_tables()
        yield
    finally:
        logger.info("Closing database connections...")
        try:
            await engine.dispose()
        except Exception as e:
            logger.error(f"Failed to close database connection: {e}.")
            raise DatabaseConnectionError(message=str(e))


app = FastAPI()


@app.get("/health")
async def health_check() -> JSONResponse:
    """Returns dict IOT support FastAPI health checks."""
    try:
        with engine.connect() as connection:
            cursor = connection.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
        db_status = "OK"
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}.")
        db_status = "DOWN"

        return JSONResponse(
            content={
                "status": "UNHEALTHY",
                "database": db_status
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    return JSONResponse(
        content={
            "status": "HEALTHY",
            "database": db_status
        },
        status_code=status.HTTP_200_OK
    )

app.include_router(router_aircraft)


if __name__ == "__main__":
    base_config = BaseConfig()
    logger.info(f"Starting server on {base_config.host}:{base_config.port}")
    uvicorn.run(app="main:app", host=base_config.host, port=base_config.port, reload=base_config.reload)
