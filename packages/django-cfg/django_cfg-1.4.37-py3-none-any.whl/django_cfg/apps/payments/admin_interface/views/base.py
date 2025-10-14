"""
Base ViewSet classes for Admin Interface API.

Common functionality for all admin interface ViewSets.
"""

from datetime import timedelta

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from django_cfg.modules.django_logging import get_logger

logger = get_logger("admin_api")


class AdminBaseViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet for admin interface with staff permissions.
    
    Provides standard CRUD operations with admin-only access.
    """

    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ['-created_at']

    # Serializer classes mapping for different actions
    serializer_classes = {}

    def get_queryset(self):
        """
        Optimized queryset for admin interface.
        
        Override in subclasses to add specific optimizations.
        """
        queryset = super().get_queryset()

        # Add common optimizations for admin
        if hasattr(self.queryset.model, 'user'):
            queryset = queryset.select_related('user')

        return queryset

    def get_serializer_class(self):
        """
        Dynamic serializer selection based on action.
        """
        serializer_classes = getattr(self, 'serializer_classes', {})
        return serializer_classes.get(self.action, self.serializer_class)

    def get_serializer_context(self):
        """Enhanced context for admin serializers."""
        context = super().get_serializer_context()
        context.update({
            'is_admin': True,
            'admin_user': self.request.user,
        })
        return context

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics for this resource."""
        queryset = self.get_queryset()
        stats = {
            'total': queryset.count(),
            'recent': queryset.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
        }
        return Response(stats)


class AdminReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for admin interface.
    
    For resources that should only be viewed, not modified.
    """

    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ['-created_at']

    def get_serializer_context(self):
        """Enhanced context for admin serializers."""
        context = super().get_serializer_context()
        context.update({
            'is_admin': True,
            'admin_user': self.request.user,
        })
        return context


class AdminTemplateViewMixin:
    """
    Mixin for template views requiring staff access.
    """

    def get_context_data(self, **kwargs):
        """Add admin-specific context."""
        from django.urls import reverse

        context = super().get_context_data(**kwargs)

        # Build navigation items for navbar
        dashboard_url = reverse('cfg_payments_admin:dashboard')
        payments_url = reverse('cfg_payments_admin:payment-list')
        webhooks_url = reverse('cfg_payments_admin:webhook-dashboard')

        payment_nav_items = [
            {
                'label': 'Dashboard',
                'url': dashboard_url,
                'active': self.request.path == dashboard_url or self.request.path.rstrip('/') == dashboard_url.rstrip('/'),
            },
            {
                'label': 'Payments',
                'url': payments_url,
                'active': self.request.path.startswith(payments_url.rstrip('/')),
            },
            {
                'label': 'Webhooks',
                'url': webhooks_url,
                'active': self.request.path.startswith(webhooks_url.rstrip('/')),
            },
        ]

        context.update({
            'is_admin_interface': True,
            'admin_user': self.request.user,
            'payment_nav_items': payment_nav_items,
        })
        return context
