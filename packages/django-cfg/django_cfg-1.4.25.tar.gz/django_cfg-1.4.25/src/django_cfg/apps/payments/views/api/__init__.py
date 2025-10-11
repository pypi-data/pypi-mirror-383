"""
API ViewSets for the Universal Payment System v2.0.

Django REST Framework ViewSets with service layer integration and nested routing.
"""

# Base ViewSets
# API Key ViewSets
from .api_keys import (
    APIKeyCreateView,
    APIKeyValidateView,
    APIKeyViewSet,
    UserAPIKeyViewSet,
)

# Balance ViewSets
from .balances import (
    TransactionViewSet,
    UserBalanceViewSet,
    UserTransactionViewSet,
)
from .base import PaymentBaseViewSet

# Currency ViewSets
from .currencies import (
    CurrencyConversionView,
    CurrencyRatesView,
    CurrencyViewSet,
    NetworkViewSet,
    ProviderCurrencyViewSet,
    SupportedCurrenciesView,
)

# Payment ViewSets
from .payments import (
    PaymentCreateView,
    PaymentStatusView,
    PaymentViewSet,
    UserPaymentViewSet,
)

# Subscription ViewSets
from .subscriptions import (
    EndpointGroupViewSet,
    SubscriptionViewSet,
    TariffViewSet,
    UserSubscriptionViewSet,
)

# Webhook ViewSets
from .webhooks import (
    UniversalWebhookView,
    supported_providers,
    webhook_handler,
    webhook_health_check,
    webhook_stats,
)

__all__ = [
    # Base
    'PaymentBaseViewSet',

    # Payment ViewSets
    'PaymentViewSet',
    'UserPaymentViewSet',
    'PaymentCreateView',
    'PaymentStatusView',

    # Balance ViewSets
    'UserBalanceViewSet',
    'TransactionViewSet',
    'UserTransactionViewSet',

    # Subscription ViewSets
    'SubscriptionViewSet',
    'UserSubscriptionViewSet',
    'EndpointGroupViewSet',
    'TariffViewSet',

    # Currency ViewSets
    'CurrencyViewSet',
    'NetworkViewSet',
    'ProviderCurrencyViewSet',
    'CurrencyConversionView',
    'CurrencyRatesView',
    'SupportedCurrenciesView',

    # API Key ViewSets
    'APIKeyViewSet',
    'UserAPIKeyViewSet',
    'APIKeyCreateView',
    'APIKeyValidateView',

    # Webhook ViewSets
    'UniversalWebhookView',
    'webhook_handler',
    'webhook_health_check',
    'webhook_stats',
    'supported_providers',
]
