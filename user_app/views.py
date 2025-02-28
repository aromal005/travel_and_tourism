from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from travel_agent.models import TravelPackage, Itinerary
import os
from django.http import JsonResponse
from datetime import datetime, timedelta
import requests
from collections import defaultdict
from travel_agent.models import Category
from . models import Blog, Wishlist
from common.models import CustomUser
from django.contrib.auth.decorators import login_required
import google.generativeai as genai
from django.conf import settings
genai.configure(api_key=settings.GEMINI_API_KEY)

CustomUser = get_user_model()

# Create your views here.

def home(request):
    return render(request, 'user/index.html')

def about(request):
    return render(request, 'user/about.html')

def service(request):
    return render(request, 'user/service.html')

def package(request):
    packages = TravelPackage.objects.select_related('travel_agent__travelagentprofile').prefetch_related('itineraries').all()
    
    for package in packages:
        for itinerary in package.itineraries.all():  # Access related itineraries
            pass
    return render(request, 'user/package.html',{"packages":packages})

def blog(request):
    blogs = Blog.objects.all()
    return render(request, 'user/blog.html', {"blogs":blogs})

def contact(request):
    return render(request, 'user/contact.html')

def single(request):
    return render(request, 'user/single.html')

def testimonial(request):
    return render(request, 'user/testimonial.html')

def guide(request):
    return render(request, 'user/guide.html')

def destination(request):
    return render(request, 'user/destination.html')

@login_required
def profile(request):
    return render(request, 'user/profile.html')


def package_detail(request,pid):
    package = get_object_or_404(TravelPackage, id=pid)
    return render(request, 'user/package-detail.html', {'package': package})

#USER PROFILE

def weather_updates(request):
    city = request.GET.get("city", "")  # Get city from request
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not city:
        return render(request, "user/weather_updates.html")  # Show form when no city is entered

    if not api_key:
        return JsonResponse({"error": "API key is missing"}, status=500)

    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        daily_forecasts = defaultdict(list)

        # Organize forecasts by date
        for item in data["list"]:
            forecast_date = datetime.utcfromtimestamp(item["dt"]).strftime('%Y-%m-%d')
            daily_forecasts[forecast_date].append(item)

        forecast_data = []
        alert_message = "✅ Safe to travel! No severe weather conditions detected."

        # Pick the midday forecast (12:00 PM) for each day
        for date, forecasts in daily_forecasts.items():
            midday_forecast = next((f for f in forecasts if "12:00:00" in f["dt_txt"]), forecasts[0])
            temp = midday_forecast["main"]["temp"]
            condition = midday_forecast["weather"][0]["description"]
            humidity = midday_forecast["main"]["humidity"]
            wind_speed = midday_forecast["wind"]["speed"] 

            # Generate alerts based on conditions
            if "storm" in condition or "heavy rain" in condition or "extreme" in condition:
                alert_message = "⚠️ Warning: Severe weather expected! Consider rescheduling your plans."
            elif temp > 40:
                alert_message = "🌡️ Warning: Extreme heat conditions! Stay hydrated and avoid outdoor activities."
            elif temp < 5:
                alert_message = "❄️ Warning: Very cold temperatures! Dress warmly and check for snowfall disruptions."
            elif "rain" in condition:
                alert_message = "☔ Advisory: Rainy conditions expected. Carry an umbrella and plan accordingly."

            forecast_data.append({
                "date": date,
                "temperature": temp,
                "condition": condition,
                "humidity": humidity,
                "wind_speed": wind_speed
            })

        return render(request, "user/weather_updates.html", {"city": city, "forecast": forecast_data, "alert": alert_message})

    return JsonResponse({"error": "City not found"}, status=404)

@login_required
def user_blog(request):
    blogs = Blog.objects.filter(author=request.user)  # Filter blogs by logged-in user
    return render(request, 'user/user_blog.html', {"blogs": blogs})

def add_blog(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        content = request.POST.get("content")
        category_id = request.POST.get("category")
        image = request.FILES.get("image")
        author = request.user  # Ensure user is logged in

        if category_id:
            category = Category.objects.get(id=category_id)
        else:
            category = None

        Blog.objects.create(
            author=author,
            title=title,
            description=description,
            content=content,
            image=image,
            category=category
        )

        return redirect("user_blog")  # Redirect to blog list page after creation

    categories = Category.objects.all()

    return render(request, 'user/add_blog.html',{"categories": categories})

def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    # Check if the logged-in user is the author of the blog
    if blog.author != request.user:
        messages.error(request, "You are not authorized to delete this blog.")
        return redirect("user_blog")  # Redirect to blog list

    if request.method == "POST":
        blog.delete()
        messages.success(request, "Blog deleted successfully.")
        return redirect("user_blog")  # Redirect to the same blog list page
    return redirect('blog_list')

def edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    if request.method == "POST":
        blog.title = request.POST.get('title')
        blog.description = request.POST.get('description')
        blog.content = request.POST.get('content')
        
        if 'image' in request.FILES:
            blog.image = request.FILES['image']

        blog.save()
        return redirect('user_blog')  # Redirect back to blog list after editing

    return render(request, 'user/edit_blog.html', {'blog': blog})

def add_to_wishlist(request, package_id):
    package = get_object_or_404(TravelPackage, id=package_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, package=package)
    print(f"Added: {created}, Wishlist: {wishlist_item}")

    if not created:
        wishlist_item.delete()
        return JsonResponse({"status": "removed","message": "Removed from wishlist"})

    return JsonResponse({"status": "added", "message": "Added to wishlist"})

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'user/wishlist.html', {"wishlist_items": wishlist_items})



import logging

# Configure logging
logger = logging.getLogger(__name__)

def generate_ai_itinerary(request):
    package_name = request.GET.get("package_name", "Unknown Package")
    destination = request.GET.get("destination", "Unknown Destination")

    try:
        days = int(request.GET.get("days", 3))
    except ValueError:
        logger.warning("Invalid value for days. Defaulting to 3.")
        days = 3  

    prompt = f"""
    Generate a detailed travel itinerary for {days} days for a trip to {destination}.
    Each day should include:
    - Morning, afternoon, and evening activities.
    - Must-visit attractions, local experiences, and food recommendations.
    - Travel tips and cultural insights.

    Format response as:
    **Day 1:** Activity details
    **Day 2:** Activity details
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)

        # Debugging: Print full response
        print("Full AI Response:", response)

        # Extract text from response
        if response and response.candidates and response.candidates[0].content.parts:
            ai_text = response.candidates[0].content.parts[0].text.strip()
        else:
            logger.error("Unexpected AI response format.")
            return JsonResponse({"error": "Unexpected AI response format"}, status=500)

        # Process response into structured itinerary
        itinerary = []
        lines = ai_text.split("\n")

        day = None
        activities = []

        for line in lines:
            line = line.strip()
            if line.lower().startswith("**day"):  # Detect new day
                if day and activities:
                    itinerary.append({"day": day, "activities": activities})
                day = line.replace("**", "").strip()  # Remove bold markers
                activities = []
            elif day:
                activities.append(line)  # Append activities to current day

        # Add last day's data
        if day and activities:
            itinerary.append({"day": day, "activities": activities})

        if not itinerary:
            logger.error("Failed to extract itinerary from AI response.")
            return JsonResponse({"error": "Failed to extract itinerary"}, status=500)

        logger.info(f"Successfully generated itinerary for {destination} ({days} days).")
        return JsonResponse({"itinerary": itinerary})

    except Exception as e:
        logger.exception("Error generating AI itinerary")
        return JsonResponse({"error": str(e)}, status=500)