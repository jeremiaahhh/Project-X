# Setup Guide

## System Requirements

- Python 3.9 or higher
- Node.js 18+ (bundled npm)
- Internet access for Yahoo Finance data pulls

## 1. Clone the repository

```bash
git clone <repository-url>
cd Project-X
```

## 2. Python environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Verify core libraries

```bash
python - <<'PY'
import pandas, yfinance, fastapi
print('Backend dependencies ready')
PY
```

## 3. Frontend environment

```bash
cd frontend
npm install
cd ..
```

Copy the example environment file and adjust as required:

```bash
cp frontend/.env.example frontend/.env
```

## 4. Run the services locally

Open two shells.

**Backend**

```bash
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

**Frontend**

```bash
cd frontend
npm run dev
```

Dashboard: `http://localhost:5173` — API docs: `http://localhost:8000/docs`

## 5. Example commands

### Python script invocation

```bash
python example_usage.py
```

### CURL request to API

```bash
curl -X POST http://localhost:8000/api/v1/valuation \
  -H "Content-Type: application/json" \
  -d '{
        "ticker": "AAPL",
        "risk_free_rate": 0.04,
        "market_risk_premium": 0.06,
        "terminal_growth_rate": 0.03,
        "projection_years": 5,
        "growth_rates": [0.1,0.08,0.06,0.05,0.04],
        "peer_tickers": ["MSFT","GOOGL","AMZN"]
      }'
```

## Troubleshooting

| Issue                        | Resolution                                                                           |
| ---------------------------- | ------------------------------------------------------------------------------------ |
| `ModuleNotFoundError`        | Activate the virtual environment before running Python commands.                     |
| `ECONNREFUSED` from frontend | Ensure the FastAPI service is running on the port referenced by `VITE_API_BASE_URL`. |
| Empty peer analysis          | Provide at least one valid peer ticker; Yahoo Finance may omit some symbols.         |
| Yahoo Finance throttling     | Wait a minute and retry; batching multiple analyses may require caching.             |

## Optional: Dockerised workflow

Create `docker-compose.yml` similar to:

```yaml
services:
  api:
    build: .
    command: uvicorn backend.main:app --host 0.0.0.0 --port 8000
    env_file:
      - .env
    ports:
      - "8000:8000"
  frontend:
    build: ./frontend
    command: npm run dev -- --host --port 5173
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api/v1
```

(Provided as a starting point; tailor to your deployment strategy.)

## Tooling Suggestions

- VS Code with Python, Pylance, and Tailwind CSS IntelliSense extensions
- `npm run lint` / `npm run build` for frontend quality checks
- `ruff` or `black` (optional) for Python style

## Support

1. Review [README.md](README.md) and [DOCUMENTATION.md](DOCUMENTATION.md)
2. Check that both environments are installed correctly
3. Confirm API credentials (if you add secure endpoints)
4. Open an issue with reproduction steps if problems persist
