"""API route definitions for valuation dashboard."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas.valuation import ValuationRequest, ValuationResponse
from ..services.analysis_service import run_full_analysis

router = APIRouter(prefix="/api/v1", tags=["valuation"])


@router.get("/health", summary="Service health check")
def health_check() -> dict:
    """Simple service health probe."""
    return {"status": "ok"}


@router.post("/valuation", response_model=ValuationResponse, summary="Run full valuation analysis")
def perform_valuation(request: ValuationRequest) -> ValuationResponse:
    """Execute the valuation workflow using provided parameters."""
    try:
        payload = run_full_analysis(
            ticker=request.ticker,
            risk_free_rate=request.risk_free_rate,
            market_risk_premium=request.market_risk_premium,
            terminal_growth_rate=request.terminal_growth_rate,
            projection_years=request.projection_years,
            growth_rates=request.growth_rates,
            peer_tickers=request.peer_tickers,
        )
        return ValuationResponse(**payload)
    except Exception as exc:  # pragma: no cover - bubble up for global handler/logging
        raise HTTPException(status_code=500, detail=str(exc)) from exc
