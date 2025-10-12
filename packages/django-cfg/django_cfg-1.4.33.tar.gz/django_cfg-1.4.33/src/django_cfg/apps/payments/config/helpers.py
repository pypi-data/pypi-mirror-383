"""
Configuration helpers for the Universal Payment System v2.0.

Provides specialized helpers for different configuration aspects.
"""

from typing import Any, Dict

from django.conf import settings

from django_cfg.modules.django_logging import get_logger

from .django_cfg_integration import PaymentsConfigMixin

logger = get_logger("payments_config_helpers")


class MiddlewareConfigHelper(PaymentsConfigMixin):
    """Helper for middleware configuration."""

    @classmethod
    def get_middleware_config(cls) -> Dict[str, Any]:
        """Get middleware configuration from BaseCfgAutoModule."""
        config = cls.get_payments_config()

        return {
            # All settings from BaseCfgAutoModule (django-cfg)
            'enabled': config.enabled and config.middleware_enabled,
            'api_prefixes': getattr(config, 'api_prefixes', ['/api/']),
            'protected_paths': config.protected_paths,
            'protected_patterns': config.protected_patterns,
            'rate_limiting_enabled': config.rate_limiting_enabled,
            'default_rate_limits': config.default_rate_limits,
            'usage_tracking_enabled': config.usage_tracking_enabled,
            'track_anonymous_usage': config.track_anonymous_usage,
            'cache_timeouts': config.cache_timeouts,

            # Provider API configurations
            'enabled_providers': config.get_enabled_providers(),
            'provider_configs': {
                provider: config.get_provider_api_config(provider)
                for provider in config.get_enabled_providers()
            },
        }


class CacheConfigHelper(PaymentsConfigMixin):
    """Helper for cache configuration."""

    @classmethod
    def get_cache_backend_type(cls) -> str:
        """Get Django cache backend type."""
        django_cache = getattr(settings, 'CACHES', {}).get('default', {})
        backend = django_cache.get('BACKEND', '').lower()

        if 'redis' in backend:
            return 'redis'
        elif 'memcached' in backend:
            return 'memcached'
        elif 'database' in backend:
            return 'database'
        elif 'dummy' in backend:
            return 'dummy'
        else:
            return 'unknown'

    @classmethod
    def is_cache_enabled(cls) -> bool:
        """Check if cache is properly configured (not dummy)."""
        return cls.get_cache_backend_type() != 'dummy'

    @classmethod
    def get_cache_timeout(cls, operation: str) -> int:
        """Get cache timeout for specific operation."""
        config = cls.get_payments_config()
        return config.cache_timeouts.get(operation, config.cache_timeouts['default'])


class RedisConfigHelper(PaymentsConfigMixin):
    """Helper for Redis configuration."""

    @classmethod
    def get_redis_config(cls) -> Dict[str, Any]:
        """Get Redis configuration for payments."""
        # Default Redis settings
        redis_config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'decode_responses': True,
            'socket_timeout': 5,
            'socket_connect_timeout': 5,
            'retry_on_timeout': True,
            'health_check_interval': 30,
        }

        # Try to get Redis settings from Django CACHES
        django_cache = getattr(settings, 'CACHES', {}).get('default', {})
        if 'redis' in django_cache.get('BACKEND', '').lower():
            location = django_cache.get('LOCATION', '')
            if location.startswith('redis://'):
                # Parse redis://host:port/db format
                try:
                    # Simple parsing for redis://host:port/db
                    parts = location.replace('redis://', '').split('/')
                    host_port = parts[0].split(':')
                    redis_config['host'] = host_port[0]
                    if len(host_port) > 1:
                        redis_config['port'] = int(host_port[1])
                    if len(parts) > 1:
                        redis_config['db'] = int(parts[1])
                except (ValueError, IndexError) as e:
                    logger.warning(f"Failed to parse Redis URL {location}: {e}")

        return redis_config

    @classmethod
    def is_redis_available(cls) -> bool:
        """Check if Redis is available and configured."""
        try:
            import redis
            config = cls.get_redis_config()
            client = redis.Redis(**config)
            client.ping()
            return True
        except Exception as e:
            logger.debug(f"Redis not available: {e}")
            return False
