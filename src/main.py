# Third party imports
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Internal imports
from src.config.database import engine
from src.router.api import router as router_aircraft
from src.utils.init_db import create_tables

load_dotenv(".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config():
    return {
        "host": os.getenv("HOST", "127.0.0.1"),
        "port": int(os.getenv("PORT", 8000)),
        "reload": os.getenv("RELOAD", True),
    }


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
            status_code=503
        )

    return JSONResponse(
        content={
            "status": "HEALTHY",
            "database": db_status
        },
        status_code=200
    )

app.include_router(router_aircraft)


if __name__ == "__main__":
    config = load_config()
    logger.info(f"Starting server on {config['host']}:{config['port']}")
    uvicorn.run(app="main:app", host=config["host"], port=config["port"], reload=config["reload"])
