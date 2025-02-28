from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, TravelAgentProfile

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = "user"  # Set user type explicitly in the view, not here
        if commit:
            user.save()
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
