"""Pydantic schemas for valuation API."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, validator


class ValuationRequest(BaseModel):
    ticker: str = Field(..., description="Ticker symbol", example="AAPL")
    risk_free_rate: float = Field(0.04, ge=0, le=0.2, description="Risk free rate as decimal")
    market_risk_premium: float = Field(0.06, ge=0, le=0.3, description="Market risk premium")
    terminal_growth_rate: float = Field(0.03, ge=-0.05, le=0.1, description="Terminal growth rate")
    projection_years: int = Field(5, ge=3, le=10, description="Number of forecast years")
    growth_rates: Optional[List[float]] = Field(None, description="Annual FCF growth rates as decimals")
    peer_tickers: Optional[List[str]] = Field(None, description="List of peer ticker symbols")

    @validator('ticker')
    def _upper_ticker(cls, value: str) -> str:  # noqa: D401
        """Normalise ticker to uppercase."""
        value = value.strip()
        if not value:
            raise ValueError("Ticker must not be empty")
        return value.upper()

    @validator('growth_rates', each_item=True)
    def _validate_growth_rates(cls, value: float) -> float:  # noqa: D401
        """Ensure growth rates are within sensible bounds."""
        if value < -1 or value > 1:
            raise ValueError("Growth rates must be between -1 and 1")
        return value

    @validator('peer_tickers')
    def _normalise_peer_tickers(cls, value: Optional[List[str]]) -> Optional[List[str]]:  # noqa: D401
        """Normalise peer tickers to uppercase and deduplicate."""
        if not value:
            return None
        cleaned = []
        for ticker in value:
            ticker = ticker.strip().upper()
            if ticker and ticker not in cleaned:
                cleaned.append(ticker)
        return cleaned or None


class MetricValue(BaseModel):
    year: Optional[int]
    fcf: Optional[float]
    growth_rate: Optional[float]
    discount_factor: Optional[float]
    pv_of_fcf: Optional[float]


class ValuationResponse(BaseModel):
    inputs: dict
    company: dict
    wacc: dict
    dcf: dict
    projected_fcfs: List[MetricValue]
    discounted_fcfs: List[MetricValue]
    trading_comps: dict
    historical_prices: List[dict]
