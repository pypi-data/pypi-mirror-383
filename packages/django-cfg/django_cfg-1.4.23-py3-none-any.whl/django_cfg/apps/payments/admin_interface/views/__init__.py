"""
Admin Interface Views for Universal Payment System v2.0.

DRF ViewSets and template views for admin dashboard and management interfaces.
"""

# Template Views
# API ViewSets
from .api import (
    AdminPaymentViewSet,
    AdminStatsViewSet,
    AdminUserViewSet,
    AdminWebhookEventViewSet,
    AdminWebhookViewSet,
    WebhookTestViewSet,
)
from .dashboard import PaymentDashboardView, WebhookDashboardView
from .forms import PaymentDetailView, PaymentFormView, PaymentListView

__all__ = [
    # Template Views
    'PaymentDashboardView',
    'WebhookDashboardView',
    'PaymentFormView',
    'PaymentDetailView',
    'PaymentListView',

    # API ViewSets
    'AdminPaymentViewSet',
    'AdminWebhookViewSet',
    'AdminWebhookEventViewSet',
    'WebhookTestViewSet',
    'AdminStatsViewSet',
    'AdminUserViewSet',
]
