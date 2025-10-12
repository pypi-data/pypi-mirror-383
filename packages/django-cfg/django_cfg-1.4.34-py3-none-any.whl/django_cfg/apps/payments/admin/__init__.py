"""
Payment admin interfaces using Django Admin Utilities.

Modern, clean admin interfaces with Material Icons and no HTML duplication.
"""

from django.contrib import admin

from .api_keys_admin import APIKeyAdmin

# Import all admin classes
from .balance_admin import TransactionAdmin, UserBalanceAdmin
from .currencies_admin import CurrencyAdmin  # Use working version
from .endpoint_groups_admin import EndpointGroupAdmin
from .networks_admin import NetworkAdmin, ProviderCurrencyAdmin
from .payments_admin import UniversalPaymentAdmin
from .subscriptions_admin import SubscriptionAdmin
from .tariffs_admin import TariffAdmin, TariffEndpointGroupAdmin

# All models are registered in their respective admin files using @admin.register
# This provides:
# - Clean separation of concerns
# - Material Icons integration
# - Type-safe configurations
# - Performance optimizations
# - No HTML duplication
