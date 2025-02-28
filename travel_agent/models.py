from django.db import models
from common.models import CustomUser

# Create your models here.
class TravelPackage(models.Model):  
    package_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField()
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