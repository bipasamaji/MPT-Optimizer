# MPT-Optimizer

Modern Portfolio Theory (MPT) optimizer built with a Django backend and a React frontend. It ingests historical price data, computes expected returns and covariances, then uses convex optimization to find portfolios that minimize risk for a given target return. The app also generates the Efficient Frontier and provides a UI for exploring recommended allocations.

**Who This Helps**
- **Retail investors:** get a data-driven allocation suggestion across multiple tickers.
- **Quant students & educators:** demonstrates MPT concepts end-to-end (data → stats → convex optimization → visualization).
- **Financial analysts / researchers:** prototyping and experimenting with portfolio construction.
- **Prototyping for robo-advisors:** base components for backtesting and automated allocation engines.

**What the Project Does**
- Ingests historical prices using `yfinance` and stores them in `Price` model rows.
- Converts close prices into daily returns and annualizes expected returns and covariance matrix.
- Solves a convex optimization problem (minimize portfolio variance subject to sum(weights)=1, weights >= 0, and optional target return) using `cvxpy`.
- Sweeps target returns to build the Efficient Frontier and saves a frontier plot under `media/`.
- Provides a React UI to add tickers, fetch prices, run optimization, view weights and Frontier, and inspect saved portfolios.

**Core Concepts**
- **Daily returns:** percentage change between consecutive close prices; used as the base input.
- **Expected annual return:** annualized from daily means (example: our code uses 252 trading days to scale daily returns to annual expected return).
- **Covariance matrix:** measures how assets move together; annualized from daily covariance.
- **Portfolio variance:** w^T Σ w where `w` is weight vector and Σ is annual covariance. We minimize this under constraints.
- **Efficient Frontier:** set of portfolios that provide the minimum risk for each achievable return.

**Project Workflow (end-to-end)**
1. Create or run the Django app and the React front-end (see setup below).
2. Add symbols to the database (Admin UI or front-end `Add Symbol`).
3. Fetch historical prices for those symbols (`fetch_prices` management command or front-end `Fetch Prices`).
4. Run optimization (`run_optimizer` CLI or front-end `Run Optimizer` / `Demo`).
5. View results: recommended weights, expected return, and Efficient Frontier plot.

**API Endpoints**
- `GET /api/stocks/` — list available symbols.
- `POST /api/stocks/` — add a symbol. Example (PowerShell):
```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/stocks/ -Body (@{symbol='AAPL'; name='Apple'} | ConvertTo-Json) -ContentType 'application/json'
```
- `POST /api/fetch-prices/` — fetch historical prices for a set of symbols. Body JSON: `{"symbols":"AAPL,MSFT","start":"2024-01-01","end":"2025-01-01"}`. Example:
```powershell
$payload = @{ symbols = 'AAPL,MSFT,GOOGL'; start='2024-01-01'; end='2025-01-01' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/fetch-prices/ -Body $payload -ContentType 'application/json'
```
- `POST /api/optimize/` — runs optimizer on chosen symbols and date range. Return JSON includes `symbols`, `weights`, `expected_return`, `frontier_plot` filename. Example payload same structure as `fetch-prices` plus optional `target`.
- `GET /api/portfolios/` — list saved portfolios and weights.

**Frontend (UI) — how to test from the browser**
1. Start backend and frontend (see Running below).
2. Open `http://127.0.0.1:8000/` — the React UI is served by Django in development when the Vite build is present.
3. Left panel: use **Add Symbol** to add tickers (e.g., `AAPL`, `MSFT`, `GOOGL`).
4. Right panel: choose date range and press **Fetch Prices** (this calls `fetch_prices`).
5. Press **Run Optimizer** to compute weights and display the Efficient Frontier plot.
6. Or press **Demo** to run a short workflow that adds demo symbols, fetches prices and runs the optimizer automatically.

**Interpreting results**
- **Weights:** percentage of portfolio to allocate to each asset (sums close to 100%).
- **Expected return:** reported as an annualized decimal (e.g., `0.12` = 12%). If you see very large numbers (e.g., 1e7), that indicates a data or scaling issue — check the daily returns input or that prices aren't already percent values. To debug, inspect `daily_rets.mean()` in the Django shell.
- **Volatility (x-axis of frontier):** annualized standard deviation (sqrt of w^T Σ w).
- **Solver warnings:** you may see CVXPY solver warnings like `Solution may be inaccurate`. Try another solver (OSQP/ECOS) or adjust solver options. Numeric issues sometimes occur when the covariance matrix is ill-conditioned — use more data or regularize (add a tiny diagonal value).

**Accuracy & Limitations**
- This implementation follows Markowitz MPT — it assumes returns are stationary and variance is the appropriate risk measure.
- Model limitations:
	- Past returns don't guarantee future performance.
	- Covariance estimates can be noisy with limited data.
	- No transaction costs, taxes, or liquidity considerations are modeled.
	- No short-selling by default (weights >= 0). You can modify `allow_short` in the optimizer to permit negative weights.
- Validation: test on synthetic data where the optimum is known (two-asset examples) to verify correctness before using real money.

**Troubleshooting**
- `yfinance` warnings about `auto_adjust`: these are informational — prices are downloaded successfully in most cases.
- If `fetch_prices` returns `No data for SYMBOL`, try a wider date range or verify the ticker symbol.
- If optimizer returns 400 with `no price data`, ensure `fetch_prices` successfully inserted `Price` rows for each symbol: check Django shell: `Price.objects.filter(stock__symbol='AAPL').count()`.
- If CVXPY is missing or fails to install on Windows, either install prerequisites or request the SciPy fallback optimizer (I can add it).

**Development / Running (quick commands)**
1. Backend environment (PowerShell):
```powershell
cd D:\programming\MPT-Optimizer\MPT-Optimizer\MPT
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser   # optional
```
2. Build frontend for production (so Django serves it):
```powershell
cd D:\programming\MPT-Optimizer\MPT-Optimizer\frontend
npm install
npm run build
```
3. Run Django dev server (serves React `dist/` assets in DEBUG):
```powershell
cd D:\programming\MPT-Optimizer\MPT-Optimizer\MPT
python manage.py runserver 127.0.0.1:8000
```

**Example end-to-end test (quick)**
1. Open the UI at `http://127.0.0.1:8000/`.
2. Click **Demo** (adds `AAPL,MSFT,GOOGL`, fetches prices and runs optimizer). You should see a table of weights and a frontier plot.
3. Inspect logs — you should see messages like `Imported N rows for AAPL` and a `/media/frontier_<timestamp>.png` request.

**Next steps & improvements**
- Add a SciPy-based quadratic programming fallback for environments where CVXPY is not available.
- Add unit tests and CI to validate optimizer math on synthetic datasets.
- Add portfolio backtesting support to evaluate realized returns and compare to equal-weight baselines.
- Improve frontend UX: asset search/autocomplete, progress indicators, and ability to save portfolios from the UI.

If you'd like, I can implement any of the improvements above (SciPy fallback, tests, backtesting, or UI polish). Thank you for trying the app — paste any server logs or UI errors and I will help fix them.

