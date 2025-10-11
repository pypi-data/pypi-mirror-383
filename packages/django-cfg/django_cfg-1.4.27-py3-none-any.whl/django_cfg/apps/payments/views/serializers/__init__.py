"""
Serializers for the Universal Payment System v2.0.

Django REST Framework serializers with Pydantic integration and service layer validation.
"""

# Payment serializers
# API Key serializers
from .api_keys import (
    APIKeyActionSerializer,
    APIKeyCreateSerializer,
    APIKeyDetailSerializer,
    APIKeyListSerializer,
    APIKeyStatsSerializer,
    APIKeyUpdateSerializer,
    APIKeyValidationSerializer,
)

# Balance serializers
from .balances import (
    BalanceUpdateSerializer,
    TransactionSerializer,
    UserBalanceSerializer,
)

# Currency serializers
from .currencies import (
    CurrencyConversionSerializer,
    CurrencySerializer,
    NetworkSerializer,
    ProviderCurrencySerializer,
)
from .payments import (
    PaymentCreateSerializer,
    PaymentListSerializer,
    PaymentSerializer,
    PaymentStatusSerializer,
)

# Subscription serializers
from .subscriptions import (
    EndpointGroupSerializer,
    SubscriptionCreateSerializer,
    SubscriptionListSerializer,
    SubscriptionSerializer,
    SubscriptionStatsSerializer,
    SubscriptionUpdateSerializer,
    SubscriptionUsageSerializer,
    TariffSerializer,
)

# Webhook serializers
from .webhooks import (
    NowPaymentsWebhookSerializer,
    WebhookSerializer,
)

__all__ = [
    # Payment serializers
    'PaymentSerializer',
    'PaymentCreateSerializer',
    'PaymentListSerializer',
    'PaymentStatusSerializer',

    # Balance serializers
    'UserBalanceSerializer',
    'TransactionSerializer',
    'BalanceUpdateSerializer',

    # Subscription serializers
    'SubscriptionSerializer',
    'SubscriptionCreateSerializer',
    'SubscriptionListSerializer',
    'SubscriptionUpdateSerializer',
    'SubscriptionUsageSerializer',
    'SubscriptionStatsSerializer',
    'EndpointGroupSerializer',
    'TariffSerializer',

    # Currency serializers
    'CurrencySerializer',
    'NetworkSerializer',
    'ProviderCurrencySerializer',
    'CurrencyConversionSerializer',

    # API Key serializers
    'APIKeyDetailSerializer',
    'APIKeyCreateSerializer',
    'APIKeyListSerializer',
    'APIKeyUpdateSerializer',
    'APIKeyActionSerializer',
    'APIKeyValidationSerializer',
    'APIKeyStatsSerializer',

    # Webhook serializers
    'WebhookSerializer',
    'NowPaymentsWebhookSerializer',
]
