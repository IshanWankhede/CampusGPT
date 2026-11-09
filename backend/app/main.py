from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin.router import router as admin_router
from app.auth.router import router as auth_router
from app.core.config import settings

# API documentation is only exposed in development.
# In staging and production all three endpoints return 404.
_in_development = settings.ENV == "development"

# CampusGPT FastAPI Application
app = FastAPI(
    title="CampusGPT API",
    docs_url="/docs" if _in_development else None,
    redoc_url="/redoc" if _in_development else None,
    openapi_url="/openapi.json" if _in_development else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(admin_router)


@app.get("/health")
def health_check():
    # ENV is intentionally not included in the response — environment names
    # must not be exposed in public HTTP responses.
    return {"status": "ok"}
