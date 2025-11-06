"""FastAPI application entry point for valuation backend."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router as api_router

app = FastAPI(
    title="Company Valuation API",
    description="REST API powering the Company Valuation Dashboard",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["health"])  # pragma: no cover
async def root_health() -> dict:
    """Root health endpoint for simple probes."""
    return {"status": "ok"}
