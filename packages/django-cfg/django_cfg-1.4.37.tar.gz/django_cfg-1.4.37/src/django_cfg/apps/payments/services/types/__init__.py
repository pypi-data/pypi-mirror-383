"""
Pydantic types for the Universal Payment System v2.0.

Type-safe models for inter-service communication following data typing requirements.
Uses Pydantic 2 for service layer validation and business logic.
"""

# Request types
# Data types
from .data import (
    BalanceData,
    CurrencyData,
    PaymentData,
    ProviderData,
    SubscriptionData,
    TransactionData,
)
from .requests import (
    BalanceUpdateRequest,
    CurrencyConversionRequest,
    PaymentCreateRequest,
    PaymentStatusRequest,
    SubscriptionCreateRequest,
    SubscriptionUpdateRequest,
    WebhookValidationRequest,
)

# Response types
from .responses import (
    BalanceResult,
    CurrencyConversionResult,
    PaymentResult,
    ProviderResponse,
    ServiceOperationResult,
    SubscriptionResult,
)

# Webhook types
from .webhooks import (
    NowPaymentsWebhook,
    WebhookData,
    WebhookProcessingResult,
    WebhookSignature,
)

__all__ = [
    # Request types
    'PaymentCreateRequest',
    'PaymentStatusRequest',
    'BalanceUpdateRequest',
    'SubscriptionCreateRequest',
    'SubscriptionUpdateRequest',
    'CurrencyConversionRequest',
    'WebhookValidationRequest',

    # Response types
    'PaymentResult',
    'ProviderResponse',
    'BalanceResult',
    'SubscriptionResult',
    'CurrencyConversionResult',
    'ServiceOperationResult',

    # Data types
    'PaymentData',
    'BalanceData',
    'SubscriptionData',
    'TransactionData',
    'CurrencyData',
    'ProviderData',

    # Webhook types
    'WebhookData',
    'NowPaymentsWebhook',
    'WebhookProcessingResult',
    'WebhookSignature',
]
