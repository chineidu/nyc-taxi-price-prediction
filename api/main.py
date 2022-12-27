from fastapi import APIRouter, FastAPI

from config import settings

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

root_router = APIRouter()


# Add the routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(root_router)

