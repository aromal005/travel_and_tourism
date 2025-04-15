from django.db import models
from common.models import *
from user_app.models import *
from travel_agent.models import *

# Create your models here.
class AdminNotification(models.Model):
    NOTIFICATION_TYPES = (
        ('complaint', 'Complaint'),
        ('payment', 'Payment'),
        ('subscription', 'Subscription'),
        ('general', 'General'),
    )

    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general')
    message = models.TextField()
    related_id = models.PositiveIntegerField(null=True, blank=True)  # Optional ID of related object
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_type_display()}: {self.message[:50]}"
    
class Commission(models.Model):
    SOURCE_CHOICES = (
        ('booking', 'Booking'),
        ('pro_upgrade', 'Pro Upgrade'),
    )

    admin = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'admin'},
        related_name='commissions',
        help_text="The admin receiving the commission"
    )
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        help_text="The source of the commission"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The commission amount"
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commissions',
        help_text="The booking associated with the commission, if applicable"
    )
    travel_agent = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'travel_agent'},
        related_name='pro_upgrade_commissions',
        help_text="The travel agent associated with the pro upgrade, if applicable"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the commission was recorded"
    )

    def __str__(self):
        return f"{self.amount} commission for {self.source} to {self.admin}"

    class Meta:
        verbose_name = "Commission"
        verbose_name_plural = "Commissions"