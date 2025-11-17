from datetime import date, timedelta
import numpy as np
from django.core.management.base import BaseCommand
from stocks.models import Stock, Price
from portfolios.models import Portfolio, PortfolioWeight
from analysis.services import price_df_from_prices, compute_daily_returns, annualize_return, annualize_cov, optimize_min_variance


class Command(BaseCommand):
    help = "Run optimizer for selected symbols and save a Portfolio."

    def add_arguments(self, parser):
        parser.add_argument('--symbols', type=str, required=True, help='Comma-separated symbols')
        parser.add_argument('--start', type=str, required=False, help='YYYY-MM-DD start date')
        parser.add_argument('--end', type=str, required=False, help='YYYY-MM-DD end date')
        parser.add_argument('--target', type=float, required=False, help='Target annual return (decimal, e.g., 0.12)')

    def handle(self, *args, **options):
        symbols = [s.strip().upper() for s in options['symbols'].split(',')]
        start = options.get('start')
        end = options.get('end')

        # pick a default date range if not provided
        if not end:
            end = date.today().isoformat()
        if not start:
            start = (date.today() - timedelta(days=365)).isoformat()

        qs = Price.objects.filter(stock__symbol__in=symbols, date__gte=start, date__lte=end)
        price_df = price_df_from_prices(qs)
        if price_df.empty:
            self.stdout.write(self.style.ERROR("No price data found for given symbols/date range."))
            return

        daily_rets = compute_daily_returns(price_df)
        mu_annual = annualize_return(daily_rets.mean())
        cov_annual = annualize_cov(daily_rets.cov())

        target = options.get('target')
        weights = optimize_min_variance(mu_annual.values, cov_annual.values, target_return=target)

        # Normalize small numerical noise
        weights = np.array(weights, dtype=float)
        weights = weights / weights.sum()

        p = Portfolio.objects.create(name=f"Opt {'+'.join(symbols)} {date.today().isoformat()}", target_return=target)
        for sym, w in zip(price_df.columns, weights):
            stock = Stock.objects.get(symbol=sym)
            PortfolioWeight.objects.create(portfolio=p, stock=stock, weight=float(w))

        self.stdout.write(self.style.SUCCESS(f"Saved portfolio {p.name}"))
