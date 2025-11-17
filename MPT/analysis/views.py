from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.management import call_command
from stocks.models import Stock, Price
from portfolios.models import Portfolio
from .services import price_df_from_prices, compute_daily_returns, annualize_return, annualize_cov, optimize_min_variance
from .serializers import PortfolioSerializer
import os
from django.conf import settings
from django.http import FileResponse, HttpResponse
from pathlib import Path


class StockListCreateAPIView(APIView):
	def get(self, request):
		stocks = Stock.objects.all().order_by('symbol')
		data = [{'symbol': s.symbol, 'name': s.name} for s in stocks]
		return Response(data)

	def post(self, request):
		symbol = request.data.get('symbol')
		name = request.data.get('name', '')
		if not symbol:
			return Response({'detail': 'symbol required'}, status=status.HTTP_400_BAD_REQUEST)
		symbol = symbol.strip().upper()
		stock, created = Stock.objects.get_or_create(symbol=symbol, defaults={'name': name})
		return Response({'symbol': stock.symbol, 'name': stock.name, 'created': created})


class FetchPricesAPIView(APIView):
	def post(self, request):
		symbols = request.data.get('symbols')
		start = request.data.get('start')
		end = request.data.get('end')
		if not symbols:
			return Response({'detail': 'symbols required'}, status=status.HTTP_400_BAD_REQUEST)
		# use management command to perform fetch (synchronous)
		try:
			# call_command accepts kwargs matching the add_arguments names
			kwargs = {'symbols': symbols}
			if start:
				kwargs['start'] = start
			if end:
				kwargs['end'] = end
			call_command('fetch_prices', **kwargs)
		except Exception as e:
			# return error message so the frontend can display it
			return Response({'detail': f'fetch_prices failed: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		return Response({'detail': 'fetch completed'})


class OptimizeAPIView(APIView):
	def post(self, request):
		symbols = request.data.get('symbols')
		start = request.data.get('start')
		end = request.data.get('end')
		target = request.data.get('target')
		make_plot = request.data.get('plot', True)

		if not symbols:
			return Response({'detail': 'symbols required'}, status=status.HTTP_400_BAD_REQUEST)
		syms = [s.strip().upper() for s in symbols.split(',')]
		qs = Price.objects.filter(stock__symbol__in=syms)
		if start:
			qs = qs.filter(date__gte=start)
		if end:
			qs = qs.filter(date__lte=end)

		price_df = price_df_from_prices(qs)
		if price_df.empty:
			return Response({'detail': 'no price data for given symbols/dates'}, status=status.HTTP_400_BAD_REQUEST)

		daily_rets = compute_daily_returns(price_df)
		mu_annual = annualize_return(daily_rets.mean())
		cov_annual = annualize_cov(daily_rets.cov())

		weights = optimize_min_variance(mu_annual.values, cov_annual.values, target_return=target)
		weights = weights / weights.sum()

		result = {'symbols': list(price_df.columns), 'weights': [float(w) for w in weights], 'expected_return': float((weights @ mu_annual.values))}

		if make_plot:
			# Lazy import plotting helpers so that matplotlib is only required when plotting
			from .plotting import plot_frontier, efficient_frontier
			rets, vols, w_list = efficient_frontier(mu_annual.values, cov_annual.values, optimize_min_variance, n_points=40)
			filename = plot_frontier(rets, vols)
			result['frontier_plot'] = os.path.basename(filename)

		return Response(result)


class PortfolioListAPIView(APIView):
	def get(self, request):
		qs = Portfolio.objects.all().order_by('-created_at')
		serializer = PortfolioSerializer(qs, many=True)
		return Response(serializer.data)


def index_view(request):
	"""Serve the frontend index.html if available, else a simple landing page."""
	# frontend folder is at project root sibling of this Django project
	project_root = Path(settings.BASE_DIR).parent
	# Prefer a production build in frontend/dist if present
	frontend_dist_index = project_root / 'frontend' / 'dist' / 'index.html'
	frontend_index = project_root / 'frontend' / 'index.html'
	if frontend_dist_index.exists():
		return FileResponse(open(frontend_dist_index, 'rb'), content_type='text/html')
	if frontend_index.exists():
		return FileResponse(open(frontend_index, 'rb'), content_type='text/html')
	# fallback HTML
	html = """
	<html><head><title>MPT Optimizer</title></head><body>
	<h1>MPT Optimizer</h1>
	<p>The frontend index was not built. You can run the React dev server in `frontend/`.</p>
	<ul>
	  <li><a href='/admin/'>Admin</a></li>
	  <li><a href='/api/stocks/'>API: stocks</a></li>
	</ul>
	</body></html>
	"""
	return HttpResponse(html)

