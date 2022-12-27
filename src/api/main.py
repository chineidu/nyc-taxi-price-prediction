from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# Custom imports
from src.api.config import settings, setup_app_logging
from src.api.routes import api_router


# Setup logging
setup_app_logging(config=settings)

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

root_router = APIRouter()


# Add the routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(root_router)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    host = "localhost"
    port = 8001

    # Use this for debugging purposes only
    logger.warning("Running in development mode. Do not run like this in production.")

    # Run the server
    uvicorn.run(app, host=host, port=port, log_level="debug")
