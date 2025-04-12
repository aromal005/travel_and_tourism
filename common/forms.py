import random
import string
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.core.exceptions import ValidationError


class UserRegistrationForm(UserCreationForm):
    referral_code = forms.CharField(
        max_length=10,
        required=False,
        help_text="Enter referral code (if any)"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'password1', 'password2']  # Exclude referral_code

    def clean_referral_code(self):
        """Validate the referral code if provided."""
        referral_code = self.cleaned_data.get("referral_code")
        if referral_code:
            if not CustomUser.objects.filter(referral_code=referral_code).exists():
                raise ValidationError("Invalid referral code.")
        return referral_code

    def _generate_coupon_code(self, length=8):
        """Generate a unique random coupon code."""
        while True:
            code = get_random_string(length, allowed_chars=string.ascii_uppercase + string.digits)
            if not Coupon.objects.filter(code=code).exists():
                return code

    def save(self, commit=True):
        """Save the user and handle referral code rewards."""
        user = super().save(commit=False)  # Get user instance without saving

        # Ensure referral_code is not set on the user instance
        user.referral_code = None  # Model will generate a new one

        # Get the provided referral code for coupon logic
        provided_referral_code = self.cleaned_data.get('referral_code')

        if commit:
            try:
                # Save user, which triggers model to generate new referral_code
                user.save()

                # Assign coupons if a valid referral code was provided
                if provided_referral_code:
                    referrer = CustomUser.objects.filter(referral_code=provided_referral_code).first()
                    if referrer and referrer != user:
                        # Generate unique coupon codes
                        coupon_code_user = self._generate_coupon_code()
                        coupon_code_referrer = self._generate_coupon_code()

                        # Create coupon for new user
                        Coupon.objects.create(
                            user=user,
                            code=coupon_code_user,
                            discount_percentage=15.0
                        )
                        # Create coupon for referrer
                        Coupon.objects.create(
                            user=referrer,
                            code=coupon_code_referrer,
                            discount_percentage=15.0
                        )

            except Exception as e:
                raise e

        return user


class TravelAgentRegistrationForm(UserCreationForm):
    travel_company_name = forms.CharField(max_length=255, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = "travel_agent"  # Set user type explicitly in the view, not here
        if commit:
            user.save()
            TravelAgentProfile.objects.create(user=user, travel_company_name=self.cleaned_data['travel_company_name'])
        return user
