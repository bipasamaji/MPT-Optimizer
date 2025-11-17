from django.db import models
from django.conf import settings
from stocks.models import Stock

class Portfolio(models.Model):
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    target_return = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PortfolioWeight(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='weights')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    weight = models.FloatField()

    class Meta:
        unique_together = ('portfolio', 'stock')
    def __str__(self):
        return f"{self.portfolio.name} - {self.stock.symbol}: {self.weight:.4f}"



