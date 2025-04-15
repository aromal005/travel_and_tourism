from django.db import models
from common.models import *

# Create your models here.
class TravelPackage(models.Model):  
    package_name = models.CharField(max_length=255)
    destination = models.CharField(max_length=200, default='null')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField()
    num_persons = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100, default='null')
    description = models.TextField()
    featured = models.BooleanField(default=False)
    travel_agent = models.ForeignKey(
        CustomUser,  # Use the imported CustomUser model
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'travel_agent'},
        related_name='packages',
        null=True,  # Allow NULL values temporarily
        blank=True
    )
    # latitude = models.FloatField()  # Store latitude
    # longitude = models.FloatField()
    # category = models.CharField(max_length=255)
    
    def __str__(self):
        return self.package_name
        

class Itinerary(models.Model):
    travel_package = models.ForeignKey(TravelPackage, related_name='itineraries', on_delete=models.CASCADE)
    day_number = models.PositiveIntegerField()
    activity_details = models.TextField()
    image = models.ImageField(upload_to='itinerary_images/')
    
    def __str__(self):
        return f"{self.travel_package.package_name} - Day {self.day_number}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    cat_description =models.TextField()

    def __str__(self):
        return self.name
    
class Notification(models.Model):
    travel_agent = models.ForeignKey(TravelAgentProfile, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.travel_agent.user.username}"
    
class PackageRating(models.Model):
    travel_package = models.ForeignKey(
        TravelPackage,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='package_ratings'
    )
    rating = models.PositiveIntegerField(
        choices=((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')),
        help_text="Rating from 1 to 5 stars"
    )
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('travel_package', 'user')  # Ensures one rating per user per package

    def __str__(self):
        return f"{self.rating} stars for {self.travel_package} by {self.user}"