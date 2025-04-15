from django.db import models
from common.models import CustomUser
from travel_agent.models import *

class Blog(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Links to CustomUser
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="wishlist")
    package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'package')  # Prevent duplicates

    def __str__(self):
        return f"{self.user.username} - {self.package.package_name}"
    
class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    travel_package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    travel_date = models.DateField()
    travelers_count = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Booking {self.id} - {self.user.username} ({self.status})"
    
class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class Complaint(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaints'
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    file = models.FileField(
        upload_to='complaints/files/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text="Upload an image or document related to your complaint (optional)."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('resolved', 'Resolved'),
            ('closed', 'Closed'),
        ),
        default='pending'
    )

    def __str__(self):
        return f"Complaint by {self.name} - {self.subject}"