# sentiment-crypto-lab

Production-ready, configurable crypto analysis and prediction stack.

## Stack
- Backend: FastAPI + SQLAlchemy + scikit-learn
- Frontend: Next.js (TypeScript)
- DB: SQLite by default
- Market provider interface with Binance default
- Social providers via official APIs (Twitter/X + Reddit)

## Key capabilities
- Coin-agnostic analysis for any provider-supported symbol.
- Configurable technical + sentiment features with weighted composite score.
- Prediction endpoint with confidence + top features.
- Backtesting in safe paper-trading mode.
- Runtime config layering: `defaults.yml` < env vars < DB overrides.

## macOS setup
### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[test]
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Required env vars
- `SCL_JWT_SECRET`
- `SCL_MASTER_KEY` (for provider key encryption)
- `SCL_ADMIN_USERNAME`
- `SCL_ADMIN_PASSWORD`
- Optional social keys:
  - `SCL_TWITTER_BEARER_TOKEN`
  - `SCL_REDDIT_CLIENT_ID`
  - `SCL_REDDIT_CLIENT_SECRET`
  - `SCL_REDDIT_USER_AGENT`

If social keys are missing, social sentiment gracefully degrades to empty/no-op.

## Running tests
```bash
cd backend
pytest
```

## Example flow
1. Query `/symbols?query=BTC`.
2. Analyze with `/analyze?symbol=BTCUSDT&interval=1h&limit=200`.
3. Get prediction from `/predict?symbol=BTCUSDT&interval=1h`.
4. Run `/backtest` with JSON body `{ "symbol": "BTCUSDT", "interval": "1h", "limit": 300 }`.
5. Update runtime config via admin `/config` endpoint or Admin UI.

## Optional Docker
```bash
docker compose up
```
