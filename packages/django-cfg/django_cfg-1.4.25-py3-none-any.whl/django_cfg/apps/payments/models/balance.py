"""
Balance and transaction models for the Universal Payment System v2.0.

Handles user balances and transaction history with atomic operations.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from .base import UUIDTimestampedModel

User = get_user_model()


class UserBalance(models.Model):
    """
    User balance model with atomic operations.
    
    Tracks user balance in USD (float for performance as per requirements).
    All balance updates are handled via Django signals for consistency.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='payment_balance',
        help_text="User who owns this balance"
    )

    balance_usd = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Current balance in USD (float for performance)"
    )

    reserved_usd = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Reserved amount in USD (pending transactions)"
    )

    # Tracking fields
    total_deposited = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Total amount deposited (lifetime)"
    )

    total_spent = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Total amount spent (lifetime)"
    )

    last_transaction_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the last transaction occurred"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Manager
    from .managers.balance_managers import UserBalanceManager
    objects = UserBalanceManager()

    class Meta:
        db_table = 'payments_user_balances'
        verbose_name = 'User Balance'
        verbose_name_plural = 'User Balances'
        indexes = [
            models.Index(fields=['balance_usd']),
            models.Index(fields=['last_transaction_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance_usd__gte=0.0),
                name='balance_non_negative_check'
            ),
            models.CheckConstraint(
                condition=models.Q(reserved_usd__gte=0.0),
                name='reserved_non_negative_check'
            ),
        ]

    def __str__(self):
        return f"{self.user.username}: ${self.balance_usd:.2f}"

    def clean(self):
        """Validate balance data."""
        if self.balance_usd < 0:
            raise ValidationError("Balance cannot be negative")
        if self.reserved_usd < 0:
            raise ValidationError("Reserved amount cannot be negative")

    @property
    def balance_display(self) -> str:
        """Formatted balance display."""
        return f"${self.balance_usd:.2f} USD"

    @property
    def is_empty(self) -> bool:
        """Check if balance is zero."""
        return self.balance_usd == 0.0

    @property
    def has_transactions(self) -> bool:
        """Check if user has any transactions."""
        return self.last_transaction_at is not None

    def add_funds(self, amount: float, transaction_type: str = 'deposit',
                  description: str = None, payment_id: str = None) -> 'Transaction':
        """Add funds to balance (delegates to manager)."""
        return self.__class__.objects.add_funds_to_user(
            self.user, amount, transaction_type, description, payment_id
        )

    def subtract_funds(self, amount: float, transaction_type: str = 'withdrawal',
                      description: str = None, payment_id: str = None) -> 'Transaction':
        """Subtract funds from balance (delegates to manager)."""
        return self.__class__.objects.subtract_funds_from_user(
            self.user, amount, transaction_type, description, payment_id
        )

    @classmethod
    def get_or_create_for_user(cls, user: User) -> 'UserBalance':
        """Get or create balance for user (delegates to manager)."""
        return cls.objects.get_or_create_for_user(user)




class Transaction(UUIDTimestampedModel):
    """
    Transaction record for balance changes.
    
    Immutable record of all balance changes with full audit trail.
    """

    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", "Deposit"
        WITHDRAWAL = "withdrawal", "Withdrawal"
        PAYMENT = "payment", "Payment"
        REFUND = "refund", "Refund"
        FEE = "fee", "Fee"
        BONUS = "bonus", "Bonus"
        ADJUSTMENT = "adjustment", "Adjustment"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payment_transactions',
        help_text="User who owns this transaction"
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        help_text="Type of transaction"
    )

    # Amount in USD (float for performance, positive for credits, negative for debits)
    amount_usd = models.FloatField(
        help_text="Transaction amount in USD (positive=credit, negative=debit)"
    )

    balance_after = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="User balance after this transaction"
    )

    # Reference to related payment
    payment_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        help_text="Related payment ID (if applicable)"
    )

    # Transaction details
    description = models.TextField(
        help_text="Transaction description"
    )

    # Metadata for additional information
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional transaction metadata"
    )

    # Manager
    from .managers.balance_managers import TransactionManager
    objects = TransactionManager()

    class Meta:
        db_table = 'payments_transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['transaction_type', 'created_at']),
            models.Index(fields=['payment_id']),
            models.Index(fields=['amount_usd']),
        ]

    def __str__(self):
        sign = "+" if self.amount_usd >= 0 else ""
        return f"{self.user.username}: {sign}${self.amount_usd:.2f} ({self.transaction_type})"

    def clean(self):
        """Validate transaction data."""
        if self.balance_after < 0:
            raise ValidationError("Balance after transaction cannot be negative")

    @property
    def is_credit(self) -> bool:
        """Check if this is a credit transaction."""
        return self.amount_usd > 0

    @property
    def is_debit(self) -> bool:
        """Check if this is a debit transaction."""
        return self.amount_usd < 0

    @property
    def amount_display(self) -> str:
        """Formatted amount display."""
        sign = "+" if self.amount_usd >= 0 else ""
        return f"{sign}${abs(self.amount_usd):.2f}"

    @property
    def type_color(self) -> str:
        """Get color for transaction type display."""
        colors = {
            self.TransactionType.DEPOSIT: 'success',
            self.TransactionType.PAYMENT: 'primary',
            self.TransactionType.WITHDRAWAL: 'warning',
            self.TransactionType.REFUND: 'info',
            self.TransactionType.FEE: 'secondary',
            self.TransactionType.BONUS: 'success',
            self.TransactionType.ADJUSTMENT: 'secondary',
        }
        return colors.get(self.transaction_type, 'secondary')

    def save(self, *args, **kwargs):
        """Override save to ensure immutability."""
        # Only prevent updates, not creation
        if self.pk and not kwargs.get('force_insert', False):
            # Check if this is actually an update (record exists in DB)
            if Transaction.objects.filter(pk=self.pk).exists():
                raise ValidationError("Transactions are immutable and cannot be modified")
        super().save(*args, **kwargs)
