import numpy as np
import pandas as pd

def price_df_from_prices(queryset):
    # queryset: Price objects filtered for desired symbols & date range
    # Return a DataFrame with columns = symbols, index = date, values = adjusted_close or close
    records = []
    for p in queryset.select_related('stock').order_by('date'):
        records.append((p.date, p.stock.symbol, p.adjusted_close or p.close))
    df = pd.DataFrame(records, columns=['date', 'symbol', 'price'])
    df = df.pivot(index='date', columns='symbol', values='price')
    return df

def compute_daily_returns(price_df):
    return price_df.pct_change().dropna(how='all')

def annualize_return(daily_mean, periods=252):
    return (1 + daily_mean) ** periods - 1

def annualize_cov(daily_cov, periods=252):
    return daily_cov * periods

# Optimizer using CVXPY. If cvxpy isn't available, we can implement a SciPy fallback.
def optimize_min_variance(expected_returns, cov_matrix, target_return=None, allow_short=False):
    try:
        import cvxpy as cp
    except Exception:
        raise RuntimeError("CVXPY is required for this optimizer. Install cvxpy or use the SciPy fallback.")

    n = len(expected_returns)
    w = cp.Variable(n)
    objective = cp.quad_form(w, cov_matrix)
    constraints = [cp.sum(w) == 1]
    if not allow_short:
        constraints.append(w >= 0)
    if target_return is not None:
        constraints.append(w @ expected_returns >= target_return)

    prob = cp.Problem(cp.Minimize(objective), constraints)
    prob.solve(solver=cp.SCS)  # or cp.OSQP, cp.ECOS if installed
    if w.value is None:
        raise RuntimeError("Optimization failed")
    weights = np.array(w.value).flatten()
    return weights