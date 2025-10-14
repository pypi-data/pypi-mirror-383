"""
Currency ViewSets for the Universal Payment System v2.0.

DRF ViewSets for currency management with service integration.
"""

from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django_cfg.modules.django_logging import get_logger

from ...models import Currency, Network, ProviderCurrency
from ..serializers.currencies import (
    CurrencyConversionSerializer,
    CurrencyListSerializer,
    CurrencyRatesSerializer,
    CurrencySerializer,
    NetworkSerializer,
    ProviderCurrencySerializer,
    SupportedCurrenciesSerializer,
)
from .base import ReadOnlyPaymentViewSet

logger = get_logger("currency_viewsets")


class CurrencyViewSet(ReadOnlyPaymentViewSet):
    """
    Currency ViewSet: /api/currencies/
    
    Read-only access to currency information with conversion capabilities.
    """

    # Allow POST for conversion action
    http_method_names = ['get', 'head', 'options', 'post']

    queryset = Currency.objects.filter(is_active=True)
    serializer_class = CurrencySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['currency_type', 'is_active']
    search_fields = ['code', 'name', 'symbol']
    ordering_fields = ['code', 'name', 'created_at']

    serializer_classes = {
        'list': CurrencyListSerializer,
        'retrieve': CurrencySerializer,
    }

    @action(detail=False, methods=['get'])
    def crypto(self, request):
        """
        Get only cryptocurrencies.
        
        GET /api/currencies/crypto/
        """
        cryptos = self.get_queryset().filter(currency_type='crypto')
        serializer = CurrencyListSerializer(cryptos, many=True)

        return Response({
            'currencies': serializer.data,
            'count': len(serializer.data),
            'type': 'crypto',
            'generated_at': timezone.now().isoformat()
        })

    @action(detail=False, methods=['get'])
    def fiat(self, request):
        """
        Get only fiat currencies.
        
        GET /api/currencies/fiat/
        """
        fiats = self.get_queryset().filter(currency_type='fiat')
        serializer = CurrencyListSerializer(fiats, many=True)

        return Response({
            'currencies': serializer.data,
            'count': len(serializer.data),
            'type': 'fiat',
            'generated_at': timezone.now().isoformat()
        })

    @action(detail=False, methods=['get'])
    def stable(self, request):
        """
        Get only stablecoins.
        
        GET /api/currencies/stable/
        """
        stables = self.get_queryset().filter(
            currency_type='crypto',
            code__in=['USDT', 'USDC', 'DAI', 'BUSD', 'TUSD']
        )
        serializer = CurrencyListSerializer(stables, many=True)

        return Response({
            'currencies': serializer.data,
            'count': len(serializer.data),
            'type': 'stable',
            'generated_at': timezone.now().isoformat()
        })

    @action(detail=True, methods=['get'])
    def networks(self, request, pk=None):
        """
        Get networks for specific currency.
        
        GET /api/currencies/{id}/networks/
        """
        currency = self.get_object()
        networks = Network.objects.filter(currency=currency, is_active=True)
        serializer = NetworkSerializer(networks, many=True)

        return Response({
            'currency': CurrencyListSerializer(currency).data,
            'networks': serializer.data,
            'count': len(serializer.data),
            'generated_at': timezone.now().isoformat()
        })

    @action(detail=True, methods=['get'])
    def providers(self, request, pk=None):
        """
        Get providers supporting specific currency.
        
        GET /api/currencies/{id}/providers/
        """
        currency = self.get_object()
        provider_currencies = ProviderCurrency.objects.filter(
            currency=currency,
            is_enabled=True
        )
        serializer = ProviderCurrencySerializer(provider_currencies, many=True)

        return Response({
            'currency': CurrencyListSerializer(currency).data,
            'providers': serializer.data,
            'count': len(serializer.data),
            'generated_at': timezone.now().isoformat()
        })

    @action(detail=False, methods=['post'])
    def convert(self, request):
        """
        Convert between currencies.
        
        POST /api/currencies/convert/
        """
        serializer = CurrencyConversionSerializer(data=request.data)

        if serializer.is_valid():
            result = serializer.save()
            return Response(result)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='base_currency',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Base currency code (e.g., USD)',
                required=True,
            ),
            OpenApiParameter(
                name='currencies',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Comma-separated list of target currency codes (e.g., BTC,ETH,USDT)',
                required=True,
            ),
        ],
        summary='Get exchange rates',
        description='Get current exchange rates for specified currencies',
    )
    @action(detail=False, methods=['get'])
    def rates(self, request):
        """
        Get current exchange rates.

        GET /api/currencies/rates/?base_currency=USD&currencies=BTC,ETH
        """
        serializer = CurrencyRatesSerializer(data=request.query_params)

        if serializer.is_valid():
            result = serializer.save()
            return Response(result)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='provider',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Payment provider name (e.g., nowpayments)',
                required=False,
            ),
            OpenApiParameter(
                name='currency_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Currency type filter: crypto, fiat, or stablecoin',
                required=False,
                enum=['crypto', 'fiat', 'stablecoin'],
            ),
        ],
        summary='Get supported currencies',
        description='Get list of supported currencies from payment providers',
    )
    @action(detail=False, methods=['get'])
    def supported(self, request):
        """
        Get supported currencies from providers.

        GET /api/currencies/supported/?provider=nowpayments&currency_type=crypto
        """
        serializer = SupportedCurrenciesSerializer(data=request.query_params)

        if serializer.is_valid():
            result = serializer.save()
            return Response(result)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NetworkViewSet(ReadOnlyPaymentViewSet):
    """
    Network ViewSet: /api/networks/
    
    Read-only access to blockchain network information.
    """

    queryset = Network.objects.filter(is_active=True)
    serializer_class = NetworkSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['native_currency__code', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']

    def get_queryset(self):
        """Optimize queryset with related objects."""
        return super().get_queryset().select_related('native_currency')

    @action(detail=False, methods=['get'])
    def by_currency(self, request):
        """
        Get networks grouped by currency.
        
        GET /api/networks/by_currency/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())

            networks_by_currency = {}
            for network in queryset:
                currency_code = network.native_currency.code

                if currency_code not in networks_by_currency:
                    networks_by_currency[currency_code] = {
                        'currency': CurrencyListSerializer(network.native_currency).data,
                        'networks': []
                    }

                networks_by_currency[currency_code]['networks'].append(
                    NetworkSerializer(network).data
                )

            return Response({
                'networks_by_currency': networks_by_currency,
                'total_currencies': len(networks_by_currency),
                'generated_at': timezone.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Networks by currency failed: {e}")
            return Response(
                {'error': f'Networks by currency failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProviderCurrencyViewSet(ReadOnlyPaymentViewSet):
    """
    Provider Currency ViewSet: /api/provider-currencies/
    
    Read-only access to provider-specific currency information.
    """

    queryset = ProviderCurrency.objects.filter(is_enabled=True)
    serializer_class = ProviderCurrencySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['provider', 'currency__code', 'network__code', 'is_enabled']
    search_fields = ['provider_currency_code']
    ordering_fields = ['provider', 'created_at']

    def get_queryset(self):
        """Optimize queryset with related objects and filter currencies with valid rates."""
        return super().get_queryset().select_related('currency', 'network').filter(
            currency__usd_rate__gt=0  # Only currencies with positive USD rate
        ).exclude(
            currency__usd_rate=1.0  # Exclude stablecoins (USDT, USDC, etc.) with rate = 1.0
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='provider',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by payment provider (e.g., nowpayments)',
                required=False,
            ),
        ],
        summary='Get provider currencies grouped by provider',
        description='Get provider currencies grouped by provider',
    )
    @action(detail=False, methods=['get'])
    def by_provider(self, request):
        """
        Get provider currencies grouped by provider.

        GET /api/provider-currencies/by_provider/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())

            currencies_by_provider = {}
            for provider_currency in queryset:
                provider = provider_currency.provider

                if provider not in currencies_by_provider:
                    currencies_by_provider[provider] = {
                        'provider': provider,
                        'currencies': []
                    }

                currencies_by_provider[provider]['currencies'].append(
                    ProviderCurrencySerializer(provider_currency).data
                )

            return Response({
                'currencies_by_provider': currencies_by_provider,
                'total_providers': len(currencies_by_provider),
                'generated_at': timezone.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Provider currencies by provider failed: {e}")
            return Response(
                {'error': f'Provider currencies by provider failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def limits(self, request):
        """
        Get currency limits by provider.
        
        GET /api/provider-currencies/limits/?provider=nowpayments
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())

            provider_filter = request.query_params.get('provider')
            if provider_filter:
                queryset = queryset.filter(provider=provider_filter)

            limits = {}
            for provider_currency in queryset:
                currency_code = provider_currency.currency.code
                provider = provider_currency.provider

                key = f"{provider}_{currency_code}"
                limits[key] = {
                    'provider': provider,
                    'currency': currency_code,
                    'min_amount': provider_currency.provider_min_amount_usd,
                    'max_amount': provider_currency.provider_max_amount_usd,
                    'fee_percentage': provider_currency.provider_fee_percentage,
                }

            return Response({
                'limits': limits,
                'count': len(limits),
                'generated_at': timezone.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Currency limits failed: {e}")
            return Response(
                {'error': f'Currency limits failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Standalone views for common operations
class CurrencyConversionView(generics.GenericAPIView):
    """
    Standalone currency conversion endpoint: /api/currencies/convert/
    
    Simplified endpoint for currency conversion.
    """

    serializer_class = CurrencyConversionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Convert between currencies."""
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            result = serializer.save()
            return Response(result)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrencyRatesView(generics.GenericAPIView):
    """
    Standalone currency rates endpoint: /api/currencies/rates/
    
    Simplified endpoint for getting exchange rates.
    """

    serializer_class = CurrencyRatesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get current exchange rates."""
        serializer = self.get_serializer(data=request.query_params)

        if serializer.is_valid():
            result = serializer.save()
            return Response(result)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupportedCurrenciesView(generics.GenericAPIView):
    """
    Standalone supported currencies endpoint: /api/currencies/supported/
    
    Simplified endpoint for getting supported currencies.
    """

    serializer_class = SupportedCurrenciesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get supported currencies from providers."""
        serializer = self.get_serializer(data=request.query_params)

        if serializer.is_valid():
            result = serializer.save()
            return Response(result)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
