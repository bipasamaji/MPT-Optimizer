import yfinance as yf
from django.core.management.base import BaseCommand
from stocks.models import Stock, Price
from datetime import datetime, timedelta
import pandas as pd

class Command(BaseCommand):
    help = 'Fetch historical prices for stocks in DB'

    def add_arguments(self, parser):
        parser.add_argument('--start', type=str, help='YYYY-MM-DD start date', required=False)
        parser.add_argument('--end', type=str, help='YYYY-MM-DD end date', required=False)
        parser.add_argument('--symbols', type=str, help='Comma-separated symbols to fetch', required=False)

    def handle(self, *args, **options):
        end = options.get('end') or datetime.today().strftime('%Y-%m-%d')
        start = options.get('start') or (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
        symbols = options.get('symbols')
        if symbols:
            symbols = [s.strip().upper() for s in symbols.split(',')]
            stocks = Stock.objects.filter(symbol__in=symbols)
        else:
            stocks = Stock.objects.all()

        for stock in stocks:
            df = yf.download(stock.symbol, start=start, end=end, progress=False)
            if df.empty:
                self.stdout.write(self.style.WARNING(f'No data for {stock.symbol}'))
                continue

            prices = []
            for idx, row in df.iterrows():
                prices.append(Price(
                    stock=stock,
                    date=idx.date(),
                    open=row.get('Open'),
                    high=row.get('High'),
                    low=row.get('Low'),
                    close=row.get('Close'),
                    adjusted_close=row.get('Adj Close'),
                    volume=int(row.get('Volume') or 0)
                ))
            # Bulk create; optionally handle existing duplicates
            Price.objects.bulk_create(prices, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f'Imported {len(prices)} rows for {stock.symbol}'))