from fastapi import FastAPI
from app.config import settings
from app.database import Base, engine
from app.routers import assets, relationships

# إنشاء الـ tables لو مش موجودة
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Asset Management System — DarkAtlas Attack Surface Monitoring",
)

# Routers
app.include_router(assets.router)
app.include_router(relationships.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}