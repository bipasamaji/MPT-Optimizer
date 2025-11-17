from rest_framework import serializers
from portfolios.models import Portfolio, PortfolioWeight


class PortfolioWeightSerializer(serializers.ModelSerializer):
    stock = serializers.CharField(source='stock.symbol')

    class Meta:
        model = PortfolioWeight
        fields = ('stock', 'weight')


class PortfolioSerializer(serializers.ModelSerializer):
    weights = PortfolioWeightSerializer(many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = ('id', 'name', 'target_return', 'created_at', 'weights')
