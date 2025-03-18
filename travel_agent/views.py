from django.shortcuts import get_object_or_404, render,redirect
from . models import TravelPackage,Itinerary, Category
from django.contrib import messages  # Import Django messages
from django.contrib.auth.decorators import login_required
from common.models import CustomUser, TravelAgentProfile


def travel_agent_register(request):
    return render(request, 'travel_agent/dashboard.html')

def travel_agent_login(request):
    return render(request, 'travel_agent/dashboard.html')

def travel_agent_logout(request):
    return render(request, 'travel_agent/dashboard.html')

# Create your views here.

@login_required(login_url='login')
def dashboard(request):
    username = request.user.username  # Get logged-in user's username
    return render(request, 'travel_agent/dashboard.html', {'username': username})


def manage_package(request):
    packages = TravelPackage.objects.filter(travel_agent=request.user)
    # print(packages)
    return render(request, 'travel_agent/manage_package.html',{'packages':packages})

def edit_package(request, pid):
    package = get_object_or_404(TravelPackage, id=pid)
    
    if request.method == 'POST':
        package.package_name = request.POST['package_name']
        package.price = request.POST['price']
        package.duration = request.POST['duration']
        package.description = request.POST['description']
        package.featured = 'featured' in request.POST
        
        package.save()
        return redirect('manage_package')

    return render(request, 'travel_agent/edit_package.html', {'package': package})


def view_booking(request):
    return render(request, 'travel_agent/bookings.html')

def category(request):
    categories = Category.objects.all()
    return render(request, 'travel_agent/category.html', {'categories': categories})

def create_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            Category.objects.create(name=name, cat_description=description)
        return redirect('category')
    return render(request, 'travel_agent/create_category.html')

def complaint(request):
    return render(request, 'travel_agent/complaint.html')

def view_payment(request):
    return render(request, 'travel_agent/payment.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import TravelPackage, Itinerary

@login_required
def create_package(request):
    if request.method == "POST":
        package_name = request.POST.get("package_name")
        price = request.POST.get("price")
        duration = request.POST.get("duration")
        description = request.POST.get("description")
        featured = request.POST.get("featured") == "on"  # Checkbox handling

        # Ensure only travel agents can create packages
        if request.user.user_type != "travel_agent":
            return redirect("dashboard")  # Redirect unauthorized users

        # Create Travel Package with the logged-in travel agent
        package = TravelPackage.objects.create(
            travel_agent=request.user,  # Assign logged-in travel agent
            package_name=package_name,
            price=price,
            duration=duration,
            description=description,
            featured=featured,
        )

        # Handling Itinerary Days
        day_activities = request.POST.getlist("day_activity[]")
        day_images = request.FILES.getlist("day_image[]")

        for i in range(len(day_activities)):
            Itinerary.objects.create(
                travel_package=package,
                day_number=i + 1,
                activity_details=day_activities[i],
                image=day_images[i] if i < len(day_images) else None
            )

        # return redirect("list_packages")  # Redirect after successful creation

    return render(request, "travel_agent/create_package.html")


def delete_package(request, id):
    package = get_object_or_404(TravelPackage, id=id)
    package.delete()

    messages.success(request, "Package deleted successfully!")  # Success message
    return redirect('manage_package')

@login_required
def agent_profile(request):
    if request.user.user_type != 'travel_agent':
        return render(request, '403.html')  # Redirect if not a travel agent

    travel_agent = get_object_or_404(TravelAgentProfile, user=request.user)

    context = {
        'username': request.user.username,
        'email': request.user.email,
        'phone': request.user.phone,
        'company_name': travel_agent.travel_company_name,
    }
    return render(request, 'travel_agent/agent_profile.html', context)

