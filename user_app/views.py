import json
import re
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from travel_agent.models import *
import os
from django.db.models import Count, Avg
from django import template
from django.http import JsonResponse
from datetime import datetime, timedelta
import requests
from collections import defaultdict
from travel_agent.models import Category
from . models import *
from common.models import *
from django.contrib.auth.decorators import login_required
import google.generativeai as genai
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from travel_agent . views import send_fcm_notification
import stripe
from django.core.mail import send_mail
from . tasks import send_booking_confirmation_email
genai.configure(api_key=settings.GEMINI_API_KEY)
stripe.api_key = settings.STRIPE_SECRET_KEY  # Load API key from settings
from admin_app.models import *

CustomUser = get_user_model()

# Create your views here.

def home(request):
 
    return render(request, 'user/index.html')



def about(request):
    return render(request, 'user/about.html')

def service(request):
    return render(request, 'user/service.html')

def package(request):
    packages = TravelPackage.objects.select_related('travel_agent__travelagentprofile').prefetch_related('itineraries').annotate(
        avg_rating=Avg('ratings__rating'),
        rating_count=Count('ratings')
    ).all()
    
    # Get query parameters
    destination = request.GET.get('destination', '').strip()
    no_of_persons = request.GET.get('no_of_persons')
    budget = request.GET.get('budget')
    no_of_days = request.GET.get('no_of_days')
    
    # Apply filters
    if destination:
        packages = packages.filter(destination__icontains=destination)
    
    if no_of_persons:
        try:
            no_of_persons = int(no_of_persons)
            if no_of_persons > 0:
                packages = packages.filter(num_persons__gte=no_of_persons)
        except (ValueError, TypeError):
            pass  # Ignore invalid no_of_persons
    
    if budget:
        try:
            budget = Decimal(budget)
            if budget > 0:
                packages = packages.filter(price__lte=budget)
        except (InvalidOperation, ValueError, TypeError):
            pass  # Ignore invalid budget
    
    if no_of_days:
        try:
            no_of_days = int(no_of_days)
            if no_of_days > 0:
                packages = packages.filter(duration=no_of_days)
        except (ValueError, TypeError):
            pass

    for package in packages:
        for itinerary in package.itineraries.all():  # Access related itineraries
            pass
    return render(request, 'user/package.html',{"packages":packages})

def blog(request):
    blogs = Blog.objects.all()
    category_blog_counts = Category.objects.annotate(blog_count=Count('blog'))
    recent_blogs = Blog.objects.order_by('-created_at')[:5]
    return render(request, 'user/blog.html', {"blogs":blogs, "category_blog_counts":category_blog_counts, "recent_blogs":recent_blogs})

def contact(request):
    return render(request, 'user/contact.html')

def single(request, bid):
    blog = get_object_or_404(Blog, id=bid)
    category_blog_counts = Category.objects.annotate(blog_count=Count('blog'))
    recent_blogs = Blog.objects.order_by('-created_at')[:5]
    parts = blog.content.split("[image]") 
    return render(request, 'user/single.html', {"blog":blog, "parts": parts, "category_blog_counts":category_blog_counts, "recent_blogs":recent_blogs})

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
        #print("Full AI Response:", response)

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
    
    
register = template.Library()
@register.simple_tag
def active_link(request, url_name):
    return "active" if request.resolver_match.url_name == url_name else ""


#TRAVEL NEWS ALERT
def get_travel_news(request):
    destination = request.GET.get("destination", "travel safety")  # Default if no destination is provided
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")

    if not NEWS_API_KEY:
        return JsonResponse({"error": "API Key not found"}, status=500)

    url = f"https://newsapi.org/v2/everything?q={destination} travel&language=en&apiKey={NEWS_API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if data["status"] != "ok":
            return JsonResponse({"error": "Failed to fetch news"}, status=500)

        # Extract relevant articles
        articles = [
            {
                "title": article["title"],
                "description": article["description"],
                "url": article["url"],
                "source": article["source"]["name"]
            }
            for article in data["articles"][:3]  # Limit to top 5 news items
        ]

        return JsonResponse({"news": articles})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_travel_alerts(request):
    destination = request.GET.get("destination", "global")  # Default to global alerts
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")

    if not NEWS_API_KEY:
        return JsonResponse({"error": "API Key not found"}, status=500)

    url = f"https://newsapi.org/v2/everything?q={destination} safety OR protest OR crisis OR emergency OR political unrest&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if data["status"] != "ok":
            return JsonResponse({"error": "Failed to fetch alerts"}, status=500)

        alerts = [
            {
                "title": article["title"],
                "description": article.get("description", "No description available."),
                "url": article["url"],
                "source": article["source"]["name"]
            }
            for article in data.get("articles", [])[:5]
        ]

        return JsonResponse({"alerts": alerts})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def edit_user_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        request.user.username = fullname
        request.user.email = email
        request.user.phone = phone
        request.user.save()
        
        user_profile.address = address
        user_profile.save()
        
        return JsonResponse({'success': True})
    
    return render(request, 'profile.html', {'user_profile': user_profile})

def booking(request, package_id):
    package = get_object_or_404(TravelPackage, id=package_id) 
    itineraries = package.itineraries.all()
    coupons = Coupon.objects.filter(user=request.user, is_used=False)
    #print(package) 
    return render(request, 'user/booking.html', {'package': package, "itineraries":itineraries, "coupons":coupons})


# def store_bookings(request, package_id): 
#     if request.method == "POST":
#         user = request.user  # Get the logged-in user

#         package_id = request.POST.get("package_id")
#         travel_date = request.POST.get("travel_date")
#         num_adults = int(request.POST.get("num_adults", 1))
#         num_children = int(request.POST.get("num_children", 0))
#         total_amount = request.POST.get("total_amount")

#         total_travelers = num_adults + num_children  # Calculate total travelers

#         try:
#             package = TravelPackage.objects.get(id=package_id)

#             booking = Booking.objects.create(
#                 user=user,  # Save logged-in user
#                 travel_package=package,
#                 travel_date=travel_date,
#                 travelers_count=total_travelers,
#                 total_price=total_amount,
#             )
#             return JsonResponse({"success": True})
#         except TravelPackage.DoesNotExist:
#             return JsonResponse({"success": False, "error": "Package not found."})

#     return JsonResponse({"success": False, "error": "Invalid request."})

def view_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'user/view_bookings.html', {"bookings":bookings})


@csrf_exempt
def create_checkout_session(request, package_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Parsed JSON data:", data)

            travel_date = data.get("travel_date")
            traveler_email = data.get("traveler_email")
            total_amount = data.get("total_amount")
            coupon_code = data.get("coupon_code")
            traveler_name = data.get("traveler_name")
            traveler_phone = data.get("traveler_phone")
            num_adults = data.get("num_adults")
            num_children = data.get("num_children")

            if not travel_date:
                return JsonResponse({"error": "Travel date is required"}, status=400)

            if not total_amount:
                return JsonResponse({"error": "Total amount is required"}, status=400)

            # Validate date format
            try:
                datetime.strptime(travel_date, "%Y-%m-%d")
            except ValueError:
                return JsonResponse({"error": "Invalid date format. Expected YYYY-MM-DD"}, status=400)

            # Validate total_amount
            try:
                total_amount = float(total_amount)
                if total_amount <= 0:
                    return JsonResponse({"error": "Invalid total amount"}, status=400)
            except (TypeError, ValueError):
                return JsonResponse({"error": "Total amount must be a valid number"}, status=400)

            package = get_object_or_404(TravelPackage, id=package_id)

            # Validate coupon (for security)
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(user=request.user, code=coupon_code, is_used=False)
                    discount = float(coupon.discount_percentage)  # Convert to float
                    package_price = float(package.price)  # Convert Decimal to float
                    expected_total = package_price * (100 - discount) / 100
                    if abs(total_amount - expected_total) > 0.01:
                        return JsonResponse({"error": "Total amount does not match coupon discount"}, status=400)
                except Coupon.DoesNotExist:
                    return JsonResponse({"error": "Invalid or used coupon"}, status=400)
            else:
                # No coupon; verify total_amount matches package.price
                package_price = float(package.price)  # Convert Decimal to float
                if abs(total_amount - package_price) > 0.01:
                    return JsonResponse({"error": "Total amount does not match package price"}, status=400)

            # Use total_amount from form for Stripe
            amount_in_cents = int(total_amount * 100)
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "inr",  # INR for ₹
                            "product_data": {"name": package.package_name},
                            "unit_amount": amount_in_cents,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=(
                    f"http://127.0.0.1:8000/payment/success/"
                    f"?package_id={package.id}"
                    f"&user_id={request.user.id}"
                    f"&price={total_amount}"  # Use total_amount
                    f"&travel_date={travel_date}"
                    f"&traveler_email={traveler_email or ''}"
                    f"&traveler_name={traveler_name or ''}"
                    f"&traveler_phone={traveler_phone or ''}"
                    f"&num_adults={num_adults or 0}"
                    f"&num_children={num_children or 0}"
                    f"&coupon_code={coupon_code or ''}"
                ),
                cancel_url="http://127.0.0.1:8000/payment/cancel/",
            )
            return JsonResponse({"id": session.id})

        except json.JSONDecodeError as e:
            print("JSON decode error:", str(e))
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except TravelPackage.DoesNotExist:
            return JsonResponse({"error": "Package not found"}, status=404)
        except stripe.error.StripeError as e:
            print("Stripe error:", str(e))
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            print("Unexpected error:", str(e))
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)



from datetime import datetime
from decimal import Decimal, InvalidOperation

def success_view(request):
    package_id = request.GET.get("package_id")
    user_id = request.GET.get("user_id")
    price = request.GET.get("price")
    travel_date = request.GET.get("travel_date")
    notification_email = request.GET.get("traveler_email")
    print(f"Email of traveler: {notification_email}")

    # Validate price
    try:
        price = Decimal(price)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid price format"}, status=400)

    # Validate travel_date
    if not travel_date or travel_date.lower() == "none":
        return JsonResponse({"error": "Invalid travel date"}, status=400)
    
    try:
        travel_date = datetime.strptime(travel_date, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"error": "Invalid date format. Expected YYYY-MM-DD"}, status=400)

    try:
        package = TravelPackage.objects.get(id=package_id)
        user = CustomUser.objects.get(id=user_id)

        # Save booking
        booking = Booking.objects.create(
            user=user,
            travel_package=package,
            travel_date=travel_date,  # Now correctly validated
            travelers_count=1,
            total_price=price
        )

        # Calculate and save commission for admin
        commission_rate = Decimal('0.05')  # 5% commission
        commission_amount = price * commission_rate
        admin_user = CustomUser.objects.filter(user_type='admin').first()  # Get first admin
        if admin_user:
            Commission.objects.create(
                admin=admin_user,
                source='booking',
                amount=commission_amount,
                booking=booking
            )

        travel_agent_profile = package.travel_agent.travelagentprofile
        send_fcm_notification(travel_agent_profile, booking)

        recipient_email = notification_email if notification_email else user.email

        # Send email to user asynchronously
        subject = 'Booking Confirmation'
        message = (
            f"Dear Traveler,\n\n"
            f"Your booking has been confirmed!\n"
            f"Booking ID: {booking.id}\n"
            f"Package: {package.package_name}\n"
            f"Travel Date: {travel_date}\n"
            f"Total Price: ${price}\n\n"
            f"Thank you for choosing us!\n"
            f"Travel Pro Team"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],  # Email of the user who made the booking
            fail_silently=True,  # Set to False for debugging if needed
        )

        return render(request, "user/success.html", {"package": package})

    except (TravelPackage.DoesNotExist, CustomUser.DoesNotExist):
        return JsonResponse({"error": "Invalid booking details"}, status=400)


def cancel_view(request):
    return render(request, "payment_cancel.html")

def coupon_view(request):
    # coupons = Coupon.objects.filter(user=request.user)  {"coupons":coupons}
    return render(request, 'user/coupon.html')

# Wallete details
@login_required
def wallet_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    return render(request, 'user/wallet.html', {'wallet': wallet})

@login_required
def withdraw_funds(request):
    wallet = request.user.wallet
    errors = {}

    print(f"Withdraw funds accessed by {request.user.username}, method: POST")
    print(f"Raw POST data: {request.POST}")

    amount = request.POST.get('amount')
    account_holder = request.POST.get('account_holder')
    account_number = request.POST.get('account_number')
    ifsc_code = request.POST.get('ifsc_code')

    print(f"Form data: amount={amount}, account_holder={account_holder}, "
          f"account_number={account_number}, ifsc_code={ifsc_code}")

    # Validate inputs
    if not all([amount, account_holder, account_number, ifsc_code]):
        errors['general'] = 'All fields are required.'
    else:
        # Validate amount
        try:
            amount = Decimal(amount)  # Convert to Decimal instead of float
            if amount <= 0:
                errors['amount'] = 'Amount must be greater than zero.'
            elif amount > wallet.balance:
                errors['amount'] = 'Insufficient wallet balance.'
        except (ValueError, TypeError):
            errors['amount'] = 'Invalid amount format.'

        # Validate account holder (letters and spaces)
        if not re.match(r'^[A-Za-z\s]+$', account_holder):
            errors['account_holder'] = 'Account holder name should contain only letters and spaces.'

        # Validate account number (9-18 digits)
        if not re.match(r'^\d{9,18}$', account_number):
            errors['account_number'] = 'Account number should be 9-18 digits.'

        # Validate IFSC code (e.g., ABCD0123456)
        if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc_code):
            errors['ifsc_code'] = 'Invalid IFSC code format (e.g., ABCD0123456).'

    if not errors:
        try:
            wallet.balance -= amount
            wallet.save()
            return JsonResponse({
                'success': True,
                'message': (
                    f'Withdrawal request for ₹{amount} submitted successfully. '
                    f'Bank Details: {account_holder}, {account_number}, {ifsc_code}'
                )
            })
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error processing withdrawal: {str(e)}'
            }, status=500)

    # Return errors
    return JsonResponse({
        'success': False,
        'message': 'Please correct the errors below.',
        'errors': errors
    }, status=400)

@login_required
def cancel_booking(request):
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        
        if not booking_id:
            return JsonResponse({
                'success': False,
                'message': 'Booking ID is required.'
            }, status=400)

        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Booking not found or you do not have permission to cancel it.'
            }, status=404)

        if booking.status == 'Cancelled':
            return JsonResponse({
                'success': False,
                'message': 'Booking is already cancelled.'
            }, status=400)

        # Update booking status
        booking.status = 'Cancelled'
        booking.save()

        # Credit wallet
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        refund_amount = booking.total_price
        wallet.balance += refund_amount
        wallet.save()

        # Create notification for travel agent
        try:
            travel_package = booking.travel_package
            print(f"Travel package: {travel_package.package_name}, ID: {travel_package.id}")
            print(f"Travel agent (raw): {travel_package.travel_agent}")
            if travel_package.travel_agent:
                try:
                    travel_agent_profile = TravelAgentProfile.objects.get(user=travel_package.travel_agent)
                    print(f"Agent profile: {travel_agent_profile.user.username}, Company: {travel_agent_profile.travel_company_name}, Profile ID: {travel_agent_profile.user.id}")
                    Notification.objects.create(
                        travel_agent=travel_agent_profile,
                        message=(
                            f"User {request.user.username} cancelled a booking for "
                            f"'{travel_package.package_name}' on {booking.travel_date.strftime('%Y-%m-%d')}."
                        ),
                        is_read=False
                    )
                    print(f"Notification created for agent {travel_agent_profile.user.username}")
                except TravelAgentProfile.DoesNotExist:
                    print(f"Error: No TravelAgentProfile for user {travel_package.travel_agent.username}")
            else:
                print("Error: Travel package has no travel_agent assigned")
        except Exception as e:
            print(f"Error creating notification: {str(e)}")
            # Continue even if notification fails, as it's not critical to cancellation

        return JsonResponse({
            'success': True,
            'message': f'Booking cancelled successfully. ₹{refund_amount} refunded to your wallet.'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request data.'
        }, status=400)
    except Exception as e:
        print(f"Error cancelling booking: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error cancelling booking: {str(e)}'
        }, status=500)
    
def complaint_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        file = request.FILES.get('file')

        print(f"Received POST data: name={name}, email={email}, subject={subject}, message={message}, file={file}")

        # Validate required fields
        if not all([name, email, subject, message]):
            messages.error(request, "All fields except file are required.")
            return redirect('complaint_register')

        # Create complaint
        complaint = Complaint(
            user=request.user if request.user.is_authenticated else None,
            name=name,
            email=email,
            subject=subject,
            message=message,
            file=file
        )
        complaint.save()

        # Create admin notification
        # AdminNotification.objects.create(
        #     type='complaint',
        #     message=f"New complaint from {name} ({email}): {subject}",
        #     related_id=complaint.id
        # )

        messages.success(request, "Your complaint has been submitted successfully!")
        return redirect('complaint_register')

    return render(request, 'user/contact.html')

def user_complaint_view(request):
    # Fetch complaints for the logged-in user
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')

    # Attach the latest admin response to each complaint
    for complaint in complaints:
        # Find AdminNotification where related_id matches complaint.id
        response = AdminNotification.objects.filter(
             related_id = complaint.id, type='general'
        ).order_by('-timestamp').first()  # Latest response
        complaint.response = response.message if response else None
        complaint.response_timestamp = response.timestamp if response else None

    return render(request, 'user/user_complaint_view.html', {
        'complaints': complaints
    })

def rating(request):
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        rating_value = request.POST.get('rating')
        feedback = request.POST.get('feedback')

        try:
            travel_package = TravelPackage.objects.get(id=package_id)
        except TravelPackage.DoesNotExist:
            messages.error(request, "Invalid travel package.")
            return redirect('view_bookings')

        if not rating_value:
            messages.error(request, "Please select a rating.")
            return redirect('rating')

        # Create or update the rating
        PackageRating.objects.update_or_create(
            travel_package=travel_package,
            user=request.user,
            defaults={
                'rating': rating_value,
                'feedback': feedback
            }
        )
        messages.success(request, "Thank you for your rating!")
        return redirect('view_bookings')

    # GET request: render the rating form
    package_id = request.GET.get('package_id')
    if not package_id:
        messages.error(request, "No package selected.")
        return redirect('view_bookings')

    try:
        travel_package = TravelPackage.objects.get(id=package_id)
    except TravelPackage.DoesNotExist:
        messages.error(request, "Invalid travel package.")
        return redirect('view_bookings')

    return render(request, 'user/rating.html', {'travel_package': travel_package})