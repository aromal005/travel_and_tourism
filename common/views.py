from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm, TravelAgentRegistrationForm
from user_app.views import home
from .models import CustomUser, TravelAgentProfile


User = get_user_model()


# User Registration
def register_user(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = "user"  # Explicitly set user type
            user.save()
            return redirect("login")
    else:
        form = UserRegistrationForm()
    
    return render(request, "common/register.html", {"form": form})

# Travel Agent Registration
def register_travel_agent(request):
    if request.method == "POST":
        form = TravelAgentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = "travel_agent" 
            user.save()
            TravelAgentProfile.objects.create(user=user, travel_company_name=form.cleaned_data['travel_company_name'])
            return redirect("login")
    else:
        form = TravelAgentRegistrationForm()

    return render(request, "common/travel_agent_register.html", {"form": form})

# User Login
def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            
            if user.user_type == "admin":
                return redirect("admin_dashboard")
            elif user.user_type == "travel_agent":
                return redirect("travel_agent_home")
            else:
                return redirect("home")

    return render(request, "common/login.html")

# Logout Function
def logout_view(request):
    logout(request)
    return redirect("home")
