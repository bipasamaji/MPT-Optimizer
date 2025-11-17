import numpy as np
from datetime import datetime
import os
from django.conf import settings


def portfolio_vol(weights, cov):
    return np.sqrt(weights @ cov @ weights)


def portfolio_return(weights, mu):
    return float(weights @ mu)


def efficient_frontier(mu, cov, optimize_fn, n_points=50, allow_short=False):
    mu = np.asarray(mu)
    cov = np.asarray(cov)
    min_ret, max_ret = float(mu.min()), float(mu.max())
    target_grid = np.linspace(min_ret, max_ret, n_points)
    vols, rets, weights_list = [], [], []

    for t in target_grid:
        try:
            w = optimize_fn(mu, cov, target_return=float(t), allow_short=allow_short)
            vols.append(portfolio_vol(w, cov))
            rets.append(portfolio_return(w, mu))
            weights_list.append(w)
        except Exception:
            continue
    return np.array(rets), np.array(vols), weights_list


def plot_frontier(ret_arr, vol_arr, filename=None):
    # Lazy import matplotlib so Django management commands that don't need plotting still work
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    plt.figure(figsize=(8,5))
    plt.plot(vol_arr, ret_arr, '-o', markersize=3)
    plt.xlabel('Annualized Volatility (Std Dev)')
    plt.ylabel('Annualized Return')
    plt.title('Efficient Frontier')
    plt.grid(True)

    if filename is None:
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        media_dir = getattr(settings, 'MEDIA_ROOT', None) or os.path.join(os.getcwd(), 'media')
        os.makedirs(media_dir, exist_ok=True)
        filename = os.path.join(media_dir, f'frontier_{timestamp}.png')

    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    return filename
