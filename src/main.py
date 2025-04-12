# Third party imports
from contextlib import asynccontextmanager
from logging import INFO, basicConfig, getLogger

import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

# Internal imports
from src.config.database import engine, settings
from src.exceptions import DatabaseConnectionError
from src.router.api import router as router_aircraft
from src.utils.init_db import create_tables

basicConfig(level=INFO, format="[%(levelname)s] %(message)s")
logger = getLogger()


@asynccontextmanager
async def lifespan(_: FastAPI):
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


app = FastAPI(lifespan=lifespan)


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
            content={"status": "UNHEALTHY", "database": db_status},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return JSONResponse(
        content={"status": "HEALTHY", "database": db_status},
        status_code=status.HTTP_200_OK,
    )


app.include_router(router_aircraft)


if __name__ == "__main__":
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        app="main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
