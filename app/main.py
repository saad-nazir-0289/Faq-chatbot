from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.admin import router as admin_router
from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.db.session import create_db_and_tables, engine
from app.services.faq_service import seed_faqs
from sqlmodel import Session


settings = get_settings()
static_dir = Path("app/static")
openapi_tags = [
    {"name": "health", "description": "Basic runtime health checks."},
    {"name": "chat", "description": "Chat session and FAQ endpoints."},
    {"name": "admin", "description": "Demo admin inspection endpoints."},
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        seed_faqs(session)
    yield


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    description="Structured FAQ chatbot demo with lead capture and consultation requests.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(chat_router)
app.include_router(admin_router)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")
