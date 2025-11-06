# Technical Documentation

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│ Frontend (React + Vite + Tailwind)                                  │
│  • Parameter form, charts (Recharts), dark UI                       │
│  • Talks to REST API via Axios                                      │
└───────────────▲─────────────────────────────┬──────────────────────┘
                │ HTTP (JSON)                  │
                │                              │
┌───────────────┴──────────────────────────────▼──────────────────────┐
│ Backend (FastAPI)                                                   │
│  /api/v1/valuation                                                  │
│    └─ analysis_service.run_full_analysis                            │
│       ├─ DataFetcher (yfinance)                                     │
│       ├─ WACCCalculator                                             │
│       ├─ DCFValuator                                                │
│       ├─ TradingComps                                               │
│       └─ Historical price formatter                                 │
└─────────────────────────────────────────────────────────────────────┘
```

- **frontend/** renders the dashboard supplied with JSON payloads from the API.
- **backend/app/** hosts the reusable modelling services and API surface.
- The modelling layer remains pure Python so it can be imported by scripts, tests, or other services.

## Backend Modules

All modules live in `backend/app/services/` unless noted.

### `analysis_service.py`

- Orchestrates the full valuation workflow invoked by the API.
- Normalises request parameters, estimates base FCF (via cash flow or EBITDA fallback), and composes results into serialisable dictionaries.
- Returns: company metadata, WACC, DCF outputs, trading comps, projected/discounted FCF tables, historical price series.

### `data_fetcher.py`

- Wraps `yfinance.Ticker` to fetch company information, financial statements, balance sheet, cash flow, and price history.
- Provides `get_key_metrics()` to aggregate commonly-used metrics for downstream modelling.

### `wacc_calculator.py`

- Implements CAPM-based cost of equity and after-tax cost of debt.
- Calculates WACC with equity/debt weights derived from market capitalisation and total debt.
- Supports custom risk-free rate, market risk premium, tax rate, or pre-computed cost of debt.

### `dcf_valuator.py`

- Projects free cash flows given a base FCF and list of growth rates.
- Computes terminal value using the Gordon Growth Model and discounts cash flows using WACC.
- Produces enterprise value, equity value, implied share price, and detailed PV tables.

### `trading_comps.py`

- Builds a peer set (explicit tickers or heuristic group) and fetches their metrics.
- Calculates valuation multiples (EV/EBITDA, P/E, EV/Revenue, P/S, P/B) and summarises min/median/max ranges.
- Converts enterprise-value-based multiples to implied equity values and per-share prices.

### `visualizer.py`

- Plotly utilities retained for server-side chart generation or PDF export pipelines.

### `exporter.py`

- PowerPoint (python-pptx) and PDF (ReportLab) exporters producing presentation-ready artifacts.

### Schemas (`backend/app/schemas/valuation.py`)

- Pydantic models (`ValuationRequest`, `ValuationResponse`) ensure request validation and consistent API responses.

### API router (`backend/app/api/routes.py`)

- `/api/v1/health` – service heartbeat.
- `/api/v1/valuation` – POST endpoint calling `run_full_analysis` and returning a `ValuationResponse` payload.

### Entry point (`backend/main.py`)

- Configures FastAPI app, CORS middleware, and includes the v1 router.

## Frontend Modules

### `src/lib/api.ts`

- Axios client with configurable base URL (`VITE_API_BASE_URL`).
- `runValuationAnalysis` helper posts to `/api/v1/valuation`.

### `src/components/MetricCard.tsx`

- Reusable metric tile used across summary sections.

### `src/components/SectionHeader.tsx`

- Heading bar with icon/description/actions.

### `src/App.tsx`

- Main dashboard layout: input sidebar, results sections, Recharts visualisations, peer tables.
- Manages form state, calls API, and renders response content.

## Request → Response Flow

1. **Frontend form submission** – collects ticker, WACC/DCF assumptions, growth rates, and peers.
2. **API request** – payload POSTed to `/api/v1/valuation`.
3. **Analysis service** – fetches data, computes WACC, DCF, trading comps, formats outputs.
4. **JSON response** – delivered to frontend for rendering (cards, tables, charts).

## Key Financial Formulae

- **Cost of equity (CAPM):** `Re = Rf + β × (Rm − Rf)`
- **After-tax cost of debt:** `Rd = (Interest Expense / Total Debt) × (1 − Tc)`
- **WACC:** `WACC = (E/V × Re) + (D/V × Rd)`
- **Free cash flow:** `FCF = Operating Cash Flow − Capital Expenditure`
- **Terminal value:** `TV = FCF(n+1) / (WACC − g)`
- **Enterprise value:** `Σ PV(FCF_t) + PV(Terminal Value)`

## Error Handling Considerations

- Yahoo Finance outages or rate limits -> handled with try/except returning empty frames.
- Missing financial metrics -> fallbacks (e.g., EBITDA-based FCF) to keep analysis running.
- Division by zero guards in multiple calculations and WACC weights.
- FastAPI wraps failures in HTTP 500 with descriptive message; extend with logging/middleware for production.

## Performance Notes

- Data fetcher caches `yfinance.Ticker` object per instance to avoid repeated network calls.
- Heavy computations rely on pandas/numpy vectorisation; growth rate projections and discounts operate on DataFrames.
- Recharts automatically handles responsive rendering, but payload size can be trimmed by limiting historical price points when needed.

## Extensibility

- **New API endpoints:** create a Pydantic schema and add a router in `backend/app/api/routes.py`; reuse services or add new modules under `services/`.
- **Additional multiples:** expand `TradingComps.calculate_multiples` and extend valuation ranges accordingly.
- **Frontend modules:** define new components under `src/components/` and style using Tailwind tokens defined in `tailwind.config.js`.
- **Authentication:** add FastAPI dependencies/middleware and propagate tokens through Axios interceptors.
- **Caching:** integrate Redis or in-memory caching around `run_full_analysis` for repeated tickers.

## Testing Hooks

- Unit-test services by importing them directly (e.g., with `pytest`) and mocking `yfinance` responses.
- Frontend testing can be added via Vitest/React Testing Library; snapshots help verify layout consistency.

## Known Limitations

1. Yahoo Finance availability and field completeness vary by ticker.
2. Peer discovery is heuristic; consider integrating an industry classification API for smarter cohorts.
3. Currency handling assumes USD; extend fetcher/service layers for FX conversion.
4. No persistence layer—each request pulls data live.
5. Security features (auth, throttling) are intentionally absent for rapid prototyping.

## Future Enhancements

- Sensitivity/Scenario endpoints
- Monte Carlo simulations and value-at-risk reporting
- Historical trend storage with database backing
- Automated peer screening (GICS/NAICS lookups)
- Batch valuation job scheduling
