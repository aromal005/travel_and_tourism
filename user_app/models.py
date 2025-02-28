from django.db import models
from common.models import CustomUser
from travel_agent.models import Category  # Import Category from travel_agent
from travel_agent.models import TravelPackage

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
