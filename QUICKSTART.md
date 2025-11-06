# Quick Start Guide

Launch the valuation dashboard locally in minutes.

## 1. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd frontend
npm install
cd ..
```

## 2. Configure environment variables

Copy the example file and adjust if your API will run on a different host/port:

```bash
cp frontend/.env.example frontend/.env
```

## 3. Start the services

Open two terminals:

```bash
# Backend (FastAPI)
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000

# Frontend (React + Tailwind)
cd frontend
npm run dev
```

- API docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:5173`

## 4. Run a valuation

Inside the dashboard:

1. Enter a ticker (e.g. **AAPL**).
2. Tune WACC, DCF, and growth assumptions.
3. Provide peer tickers for comparable analysis (optional).
4. Submit to generate the full valuation stack.

## 5. Use the Python services directly

```python
from backend.app.services.analysis_service import run_full_analysis

valuation = run_full_analysis(
    ticker="AAPL",
    risk_free_rate=0.04,
    market_risk_premium=0.06,
    terminal_growth_rate=0.03,
    projection_years=5,
    growth_rates=[0.10, 0.08, 0.06, 0.05, 0.04],
    peer_tickers=["MSFT", "GOOGL", "AMZN"],
)
print(valuation["dcf"]["fair_value_share_price"])
```

## Troubleshooting

- **`ModuleNotFoundError`** – ensure the virtual environment is activated before running Python commands.
- **CORS error** – check that `VITE_API_BASE_URL` matches the backend URL and that the backend is running.
- **Slow responses** – Yahoo Finance rate limits occasionally spike; retry after a short pause.

Need more? The [README](README.md) has full documentation and the [SETUP](SETUP.md) guide covers advanced configuration.
