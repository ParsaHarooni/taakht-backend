"""Taakht Backend - Item-to-Item Trading Platform.

Main application entry point for the Taakht backend API.
"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.config import close_db, init_db, settings, setup_logging
from src.middlewares.cors import setup_cors
from src.routes import items, rbac, users
from src.services.rbac import RBACService

# Setup logging
setup_logging()
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Taakht API",
    description="Item-to-Item Trading Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Taakht Backend...")

    # Initialize database
    await init_db()

    # Initialize RBAC system
    await RBACService.initialize_default_roles()

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Taakht Backend...")
    await close_db()
    logger.info("Application shutdown complete")


# Set lifespan
app.router.lifespan_context = lifespan

# Setup CORS
setup_cors(app)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Taakht API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "taakht-backend"}


# Include routers
app.include_router(users.router)
app.include_router(rbac.router)
app.include_router(items.router)

# Add additional middleware for production
if settings.ENVIRONMENT == "production":
    from fastapi.middleware.trustedhost import TrustedHostMiddleware

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )
