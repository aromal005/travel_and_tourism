from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.crypto import get_random_string

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, phone, password=None, user_type="user"):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, phone=phone, user_type=user_type)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, phone, password):
        user = self.create_user(username, email, phone, password, user_type="admin")
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('user', 'User'),
        ('travel_agent', 'Travel Agent'),
        ('admin', 'Admin'),
    )

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='user')

    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']

    def save(self, *args, **kwargs):
        if not self.pk and not self.referral_code:  # Generate only for new users
            while True:
                new_code = get_random_string(10, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789').upper()
                if not CustomUser.objects.filter(referral_code=new_code).exists():
                    self.referral_code = new_code
                    break

        try:
            super().save(*args, **kwargs)
        except Exception as e:
            raise e

    def __str__(self):
        return f"{self.username} ({self.user_type})"
    

# Travel Agent Profile (Extra Fields)
class TravelAgentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    travel_company_name = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.travel_company_name}"

# User Profile
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class Coupon(models.Model):
    name = models.CharField(max_length=255, default='Offer 15#')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="coupons")
    code = models.CharField(max_length=15, unique=True)
    discount_percentage = models.FloatField(default=15.0)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Coupon {self.code} - {self.discount_percentage}% for {self.user.username}"
