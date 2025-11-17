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
            try:
                df = yf.download(stock.symbol, start=start, end=end, progress=False)
            except Exception as e:
                # propagate exception so callers (API) can see it
                raise RuntimeError(f'yfinance failed for {stock.symbol}: {e}')

            if df is None or df.empty:
                self.stdout.write(self.style.WARNING(f'No data for {stock.symbol}'))
                continue

            # Ensure index is a DatetimeIndex and iterate rows safely
            df = df.reset_index()
            prices = []
            for row in df.itertuples(index=False):
                # row fields: Date, Open, High, Low, Close, Adj Close, Volume (depending on yfinance)
                try:
                    date_val = getattr(row, 'Date')
                except Exception:
                    date_val = row[0]

                def get_field(obj, name, idx):
                    try:
                        return getattr(obj, name)
                    except Exception:
                        try:
                            return obj[idx]
                        except Exception:
                            return None

                open_v = get_field(row, 'Open', 1)
                high_v = get_field(row, 'High', 2)
                low_v = get_field(row, 'Low', 3)
                close_v = get_field(row, 'Close', 4)
                adj_v = get_field(row, 'Adj Close', 5) or get_field(row, 'Adj_Close', 5)
                vol_v = get_field(row, 'Volume', 6)

                # Normalize NaN -> None, and safe int conversion for volume
                if pd.isna(open_v):
                    open_v = None
                if pd.isna(high_v):
                    high_v = None
                if pd.isna(low_v):
                    low_v = None
                if pd.isna(close_v):
                    close_v = None
                if pd.isna(adj_v):
                    adj_v = None

                if vol_v is None or (isinstance(vol_v, float) and pd.isna(vol_v)):
                    vol_int = None
                else:
                    try:
                        vol_int = int(vol_v)
                    except Exception:
                        vol_int = None

                prices.append(Price(
                    stock=stock,
                    date=date_val.date() if hasattr(date_val, 'date') else date_val,
                    open=open_v,
                    high=high_v,
                    low=low_v,
                    close=close_v,
                    adjusted_close=adj_v,
                    volume=vol_int
                ))

            # Bulk create; optionally handle existing duplicates
            try:
                Price.objects.bulk_create(prices, ignore_conflicts=True)
            except Exception as e:
                raise RuntimeError(f'DB bulk insert failed for {stock.symbol}: {e}')

            self.stdout.write(self.style.SUCCESS(f'Imported {len(prices)} rows for {stock.symbol}'))