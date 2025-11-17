from django.urls import path
from .views import StockListCreateAPIView, FetchPricesAPIView, OptimizeAPIView, PortfolioListAPIView

urlpatterns = [
    path('stocks/', StockListCreateAPIView.as_view(), name='api-stocks'),
    path('fetch-prices/', FetchPricesAPIView.as_view(), name='api-fetch-prices'),
    path('optimize/', OptimizeAPIView.as_view(), name='api-optimize'),
    path('portfolios/', PortfolioListAPIView.as_view(), name='api-portfolios'),
]
