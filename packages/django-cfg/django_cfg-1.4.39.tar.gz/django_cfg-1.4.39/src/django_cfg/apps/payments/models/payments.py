"""
Payment models for the Universal Payment System v2.0.

Core payment model with simplified architecture focused on NowPayments.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from .base import UUIDTimestampedModel
from .currencies import Currency, Network

User = get_user_model()


class UniversalPayment(UUIDTimestampedModel):
    """
    Universal payment model supporting all providers.
    
    Simplified v2.0 architecture focused on NowPayments with extensible design.
    Uses float for USD amounts as per requirements for performance and API compatibility.
    """

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMING = "confirming", "Confirming"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    class PaymentProvider(models.TextChoices):
        NOWPAYMENTS = "nowpayments", "NowPayments"
        # Future providers can be added here

        @classmethod
        def get_crypto_providers(cls):
            """Get list of crypto provider values."""
            return [cls.NOWPAYMENTS]

        @classmethod
        def is_crypto_provider(cls, provider_name: str) -> bool:
            """Check if provider handles cryptocurrency."""
            return provider_name in cls.get_crypto_providers()

    # User and identification
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        help_text="User who created this payment"
    )

    internal_payment_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Internal payment identifier"
    )

    # Financial information (USD as float per requirements)
    amount_usd = models.FloatField(
        validators=[MinValueValidator(1.0), MaxValueValidator(50000.0)],
        help_text="Payment amount in USD (float for performance)"
    )

    # Cryptocurrency information
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='payments',
        help_text="Payment currency"
    )

    network = models.ForeignKey(
        Network,
        on_delete=models.PROTECT,
        related_name='payments',
        null=True,
        blank=True,
        help_text="Blockchain network (for crypto payments)"
    )

    # Crypto amounts use Decimal for precision
    pay_amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Amount to pay in cryptocurrency (Decimal for precision)"
    )

    actual_amount_usd = models.FloatField(
        null=True,
        blank=True,
        help_text="Actual amount received in USD"
    )

    fee_amount_usd = models.FloatField(
        null=True,
        blank=True,
        help_text="Fee amount in USD"
    )

    # Provider information
    provider = models.CharField(
        max_length=50,
        choices=PaymentProvider.choices,
        default=PaymentProvider.NOWPAYMENTS,
        help_text="Payment provider"
    )

    provider_payment_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="Provider's payment ID"
    )

    # Payment details
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        help_text="Current payment status"
    )

    pay_address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Cryptocurrency payment address"
    )

    payment_url = models.URLField(
        null=True,
        blank=True,
        help_text="Payment page URL"
    )

    # Transaction information
    transaction_hash = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        db_index=True,
        help_text="Blockchain transaction hash"
    )

    confirmations_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of blockchain confirmations"
    )

    # Security and validation
    security_nonce = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
        help_text="Security nonce for validation"
    )

    # Timestamps
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this payment expires"
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this payment was completed"
    )

    status_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When the payment status was last changed"
    )

    # Metadata and description
    description = models.TextField(
        blank=True,
        help_text="Payment description"
    )

    callback_url = models.URLField(
        null=True,
        blank=True,
        help_text="Success callback URL"
    )

    cancel_url = models.URLField(
        null=True,
        blank=True,
        help_text="Cancellation URL"
    )

    # Structured metadata (validated by Pydantic in services)
    provider_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider-specific data (validated by Pydantic)"
    )

    webhook_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Webhook data (validated by Pydantic)"
    )

    # Manager
    from .managers.payment_managers import PaymentManager
    objects = PaymentManager()

    class Meta:
        db_table = 'payments_universal'
        verbose_name = 'Universal Payment'
        verbose_name_plural = 'Universal Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['provider_payment_id']),
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['expires_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_usd__gte=1.0),
                name='payments_min_amount_check'
            ),
            models.CheckConstraint(
                condition=models.Q(amount_usd__lte=50000.0),
                name='payments_max_amount_check'
            ),
        ]

    def __str__(self):
        return f"Payment {self.internal_payment_id} - ${self.amount_usd:.2f} {self.currency.code}"

    @property
    def qr_data(self) -> str:
        """Generate QR code data for payment."""
        if not self.pay_address:
            return None

        # For crypto payments, use proper URI format
        if self.currency and self.currency.currency_type == 'crypto':
            currency_code = self.currency.code.lower()

            if currency_code == 'btc' and self.pay_amount:
                return f"bitcoin:{self.pay_address}?amount={self.pay_amount}"
            elif currency_code == 'eth' and self.pay_amount:
                return f"ethereum:{self.pay_address}?value={self.pay_amount}"
            elif currency_code == 'ltc' and self.pay_amount:
                return f"litecoin:{self.pay_address}?amount={self.pay_amount}"

        # Default: just return the address
        return self.pay_address

    @property
    def formatted_pay_amount(self) -> str:
        """Format cryptocurrency amount with proper precision."""
        if not self.pay_amount or not self.currency:
            return "0"

        try:
            amount = float(self.pay_amount)
            currency_code = self.currency.code.upper()

            # Different precision for different currencies
            if currency_code in ['BTC', 'LTC', 'DOGE']:
                # Bitcoin-like currencies - 8 decimal places
                formatted = f"{amount:.8f}".rstrip('0').rstrip('.')
            elif currency_code in ['ETH', 'BNB', 'MATIC']:
                # Ethereum-like currencies - 6 decimal places typically
                formatted = f"{amount:.6f}".rstrip('0').rstrip('.')
            else:
                # Other currencies - 4 decimal places
                formatted = f"{amount:.4f}".rstrip('0').rstrip('.')

            return formatted if formatted else "0"

        except (ValueError, TypeError):
            return "0"

    def get_qr_code_url(self, size=200) -> str:
        """Generate QR code URL using external service."""
        if not self.qr_data:
            return None

        from urllib.parse import quote

        # Using QR Server API (free service)
        qr_data_encoded = quote(self.qr_data)
        return f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={qr_data_encoded}"

    def _detect_network_from_address(self) -> str:
        """Detect network from address format if network is not set."""
        if not self.pay_address:
            return None

        address = self.pay_address.strip()

        # Ethereum-like addresses (0x...)
        if address.startswith('0x') and len(address) == 42:
            # Try to detect from currency code
            if self.currency:
                currency_code = self.currency.code.upper()
                if 'ETH' in currency_code:
                    return 'ethereum'
                elif 'BNB' in currency_code or 'BSC' in currency_code:
                    return 'bsc'
                elif 'MATIC' in currency_code or 'POL' in currency_code:
                    return 'polygon'
                elif 'ARB' in currency_code:
                    return 'arbitrum'
                elif 'OP' in currency_code:
                    return 'optimism'
                elif 'AVAX' in currency_code:
                    return 'avalanche c-chain'
            # Default to ethereum for 0x addresses
            return 'ethereum'

        # Bitcoin addresses
        elif address.startswith(('1', '3', 'bc1')):
            return 'bitcoin'

        # Tron addresses (T...)
        elif address.startswith('T') and len(address) == 34:
            return 'tron'

        # Litecoin addresses
        elif address.startswith(('L', 'M', 'ltc1')):
            return 'litecoin'

        return None

    def get_payment_explorer_link(self) -> str:
        """Generate blockchain explorer link for transaction."""
        if not self.transaction_hash:
            return ""

        # Try to get network name
        network_name = None
        if self.network:
            network_name = self.network.name.lower() if hasattr(self.network, 'name') else str(self.network).lower()
        else:
            # Try to detect from address
            network_name = self._detect_network_from_address()

        if not network_name:
            return ""

        # Explorer URL templates for different networks
        explorer_templates = {
            'bitcoin': 'https://blockstream.info/tx/{txid}',
            'ethereum': 'https://etherscan.io/tx/{txid}',
            'tron': 'https://tronscan.org/#/transaction/{txid}',
            'polygon': 'https://polygonscan.com/tx/{txid}',
            'bsc': 'https://bscscan.com/tx/{txid}',
            'binance smart chain': 'https://bscscan.com/tx/{txid}',
            'litecoin': 'https://blockchair.com/litecoin/transaction/{txid}',
            'dogecoin': 'https://blockchair.com/dogecoin/transaction/{txid}',
            'arbitrum': 'https://arbiscan.io/tx/{txid}',
            'optimism': 'https://optimistic.etherscan.io/tx/{txid}',
            'avalanche c-chain': 'https://snowtrace.io/tx/{txid}',
            'base': 'https://basescan.org/tx/{txid}',
        }

        template = explorer_templates.get(network_name)
        if template:
            return template.format(txid=self.transaction_hash)

        return ""

    def get_address_explorer_link(self) -> str:
        """Generate blockchain explorer link for payment address."""
        if not self.pay_address:
            return ""

        # Try to get network name
        network_name = None
        if self.network:
            network_name = self.network.name.lower() if hasattr(self.network, 'name') else str(self.network).lower()
        else:
            # Try to detect from address
            network_name = self._detect_network_from_address()

        if not network_name:
            return ""

        # Explorer URL templates for address viewing
        address_explorer_templates = {
            'bitcoin': 'https://blockstream.info/address/{address}',
            'ethereum': 'https://etherscan.io/address/{address}',
            'tron': 'https://tronscan.org/#/address/{address}',
            'polygon': 'https://polygonscan.com/address/{address}',
            'bsc': 'https://bscscan.com/address/{address}',
            'binance smart chain': 'https://bscscan.com/address/{address}',
            'litecoin': 'https://blockchair.com/litecoin/address/{address}',
            'dogecoin': 'https://blockchair.com/dogecoin/address/{address}',
            'arbitrum': 'https://arbiscan.io/address/{address}',
            'optimism': 'https://optimistic.etherscan.io/address/{address}',
            'avalanche c-chain': 'https://snowtrace.io/address/{address}',
            'base': 'https://basescan.org/address/{address}',
        }

        template = address_explorer_templates.get(network_name)
        if template:
            return template.format(address=self.pay_address)

        return ""

    def get_payment_status_url(self) -> str:
        """Generate URL for payment status page in admin interface."""
        from django.urls import reverse
        return reverse('cfg_payments_admin:payment-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        """Override save to generate internal payment ID."""
        if not self.internal_payment_id:
            # Generate internal payment ID
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.internal_payment_id = f"PAY_{timestamp}_{str(self.id)[:8]}"

        super().save(*args, **kwargs)

    def clean(self):
        """Model validation."""
        # Crypto payments must have network
        if self.currency and self.currency.is_crypto and not self.network:
            raise ValidationError("Cryptocurrency payments must specify a network")

        # Fiat payments should not have network
        if self.currency and self.currency.is_fiat and self.network:
            raise ValidationError("Fiat payments should not specify a network")

        # Validate amount limits
        if self.amount_usd and (self.amount_usd < 1.0 or self.amount_usd > 50000.0):
            raise ValidationError("Payment amount must be between $1.00 and $50,000.00")

        # Validate expiration
        if self.expires_at and self.expires_at <= timezone.now():
            raise ValidationError("Expiration time must be in the future")

    # Status properties
    @property
    def is_pending(self) -> bool:
        """Check if payment is pending."""
        return self.status == self.PaymentStatus.PENDING

    @property
    def is_completed(self) -> bool:
        """Check if payment is completed."""
        return self.status == self.PaymentStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if payment failed."""
        return self.status in [
            self.PaymentStatus.FAILED,
            self.PaymentStatus.EXPIRED,
            self.PaymentStatus.CANCELLED
        ]

    @property
    def is_expired(self) -> bool:
        """Check if payment is expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    @property
    def requires_confirmation(self) -> bool:
        """Check if payment requires blockchain confirmation."""
        return self.status in [
            self.PaymentStatus.CONFIRMING,
            self.PaymentStatus.CONFIRMED
        ]

    # Display properties
    @property
    def status_color(self) -> str:
        """Get color for status display."""
        colors = {
            self.PaymentStatus.PENDING: 'warning',
            self.PaymentStatus.CONFIRMING: 'info',
            self.PaymentStatus.CONFIRMED: 'primary',
            self.PaymentStatus.COMPLETED: 'success',
            self.PaymentStatus.FAILED: 'danger',
            self.PaymentStatus.EXPIRED: 'secondary',
            self.PaymentStatus.CANCELLED: 'secondary',
            self.PaymentStatus.REFUNDED: 'warning',
        }
        return colors.get(self.status, 'secondary')

    @property
    def amount_display(self) -> str:
        """Formatted amount display."""
        return f"${self.amount_usd:.2f} USD"

    @property
    def crypto_amount_display(self) -> str:
        """Formatted crypto amount display."""
        if not self.pay_amount:
            return "N/A"
        return f"{self.pay_amount:.8f} {self.currency.code}"

    # Business logic methods
    def can_be_cancelled(self) -> bool:
        """Check if payment can be cancelled."""
        return self.status in [
            self.PaymentStatus.PENDING,
            self.PaymentStatus.CONFIRMING
        ]

    def can_be_refunded(self) -> bool:
        """Check if payment can be refunded."""
        return self.status == self.PaymentStatus.COMPLETED

    def mark_completed(self, actual_amount_usd: float = None, transaction_hash: str = None):
        """Mark payment as completed (delegates to manager)."""
        return self.__class__.objects.mark_payment_completed(
            self, actual_amount_usd, transaction_hash
        )

    def mark_failed(self, reason: str = None, error_code: str = None):
        """Mark payment as failed (delegates to manager)."""
        return self.__class__.objects.mark_payment_failed(
            self, reason, error_code
        )

    def cancel(self, reason: str = None):
        """Cancel payment (delegates to manager)."""
        return self.__class__.objects.cancel_payment(self, reason)


