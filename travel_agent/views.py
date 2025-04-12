from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from . models import *
from django.contrib import messages  # Import Django messages
from django.contrib.auth.decorators import login_required
from common.models import CustomUser, TravelAgentProfile
from django.shortcuts import render, redirect
from user_app . models import *
from firebase_admin import messaging
from django.views.decorators.csrf import csrf_exempt
import json
import firebase_admin
from firebase_admin import messaging
from .utils import *
from django.utils.dateparse import parse_date
from django.db.models import Q

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
    categories = Category.objects.all()
    
    if request.method == 'POST':
        package.package_name = request.POST['package_name']
        package.destination = request.POST['destination']
        package.price = request.POST['price']
        package.duration = request.POST['duration']
        package.num_persons = request.POST['num_persons']
        package.category = request.POST['category']
        package.description = request.POST['description']
        package.featured = 'featured' in request.POST
        
        package.save()
        return redirect('manage_package')

    return render(request, 'travel_agent/edit_package.html', {'package': package, 'categories': categories})


def view_booking(request):
    if request.user.user_type == "travel_agent":
        # Fetch bookings where the travel package belongs to the logged-in travel agent
        bookings = Booking.objects.filter(travel_package__travel_agent=request.user).order_by('-booking_date')
        
        search_query = request.GET.get('search', '')
        from_date = request.GET.get('from_date', '')
        to_date = request.GET.get('to_date', '')
        

        if search_query:
            bookings = bookings.filter(Q(user__username__icontains=search_query) | Q(travel_package__package_name__icontains=search_query))

        from_date_obj = parse_date(from_date)
        to_date_obj = parse_date(to_date)

        if from_date_obj and to_date_obj:
            bookings = bookings.filter(booking_date__date__range=(from_date_obj, to_date_obj))
        elif from_date_obj:
            bookings = bookings.filter(booking_date__date__gte=from_date_obj)
        elif to_date_obj:
            bookings = bookings.filter(booking_date__date__lte=to_date_obj)        

    else:
        # Prevent unauthorized users from accessing bookings
        bookings = Booking.objects.none()  
    return render(request, 'travel_agent/bookings.html', {'bookings': bookings, 'search_query': search_query, 'from_date': from_date, 'to_date': to_date})

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



@login_required
def create_package(request):
    categories = Category.objects.all()
    if request.method == "POST":
        package_name = request.POST.get("package_name")
        destination = request.POST.get("destination")
        price = request.POST.get("price")
        duration = request.POST.get("duration")
        num_persons = request.POST.get("num_persons")
        category = request.POST.get("category")
        description = request.POST.get("description")
        featured = request.POST.get("featured") == "on"  # Checkbox handling

        # Ensure only travel agents can create packages
        if request.user.user_type != "travel_agent":
            return redirect("dashboard")  # Redirect unauthorized users

        # Create Travel Package with the logged-in travel agent
        package = TravelPackage.objects.create(
            travel_agent=request.user,  # Assign logged-in travel agent
            destination=destination,
            package_name=package_name,
            price=price,
            duration=duration,
            num_persons=num_persons,
            category=category,
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

    return render(request, "travel_agent/create_package.html", {"categories": categories})


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

@login_required
def edit_agent_profile(request):
    user = request.user
    travel_agent_profile, created = TravelAgentProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        travel_agent_profile.travel_company_name = request.POST.get('company_name')

        if 'profile_picture' in request.FILES:
            travel_agent_profile.profile_picture = request.FILES['profile_picture']

        user.save()
        travel_agent_profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('agent_profile')

    return render(request, 'travel_agent/edit_agent_profile.html', {
        'user': user,
        'travel_agent_profile': travel_agent_profile,
    })


import logging

logger = logging.getLogger(__name__)  # Define logger

@csrf_exempt  
def update_fcm_token(request):
    if request.method == "POST" and request.user.is_authenticated:
        try:
            data = json.loads(request.body.decode("utf-8"))
            token = data.get("fcm_token")

            if not token:   
                logger.error("FCM Token is missing from request data.")
                return JsonResponse({"error": "FCM Token is required"}, status=400)

            # Check if user is a travel agent
            if hasattr(request.user, "travelagentprofile"):
                travel_agent = request.user.travelagentprofile
                travel_agent.fcm_token = token
                travel_agent.save()

                logger.info(f"FCM Token updated for user: {request.user.username}, Token: {token}")
                return JsonResponse({"message": "FCM Token Updated"})

            # Save to User Profile if it's a normal user
            if hasattr(request.user, "profile"):
                user_profile = request.user.profile
                user_profile.fcm_token = token
                user_profile.save()

                logger.info(f"FCM Token updated for User: {request.user.username}, Token: {token}")
                return JsonResponse({"message": "FCM Token Updated for User"})

            # If neither a travel agent nor a normal user profile exists, return error
            logger.warning(f"Unauthorized attempt to update FCM Token by unknown profile: {request.user.username}")
            return JsonResponse({"error": "User does not have a valid profile"}, status=403)

        except json.JSONDecodeError:
            logger.error("Invalid JSON data received.")
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    logger.error("Invalid request method or unauthenticated user.")
    return JsonResponse({"error": "Invalid request"}, status=400)

if not firebase_admin._apps:
    firebase_admin.initialize_app()

def send_fcm_notification(travel_agent, booking):
    print(f"📢 Sending notification for Travel Agent: {travel_agent}")  # Debugging Line

    if not travel_agent.fcm_token:
        print("⚠️ No FCM Token Found")  # Debugging Line
        return None  # Exit early if no token is available

    message = messaging.Message(
        token=travel_agent.fcm_token,
        notification=messaging.Notification(
            title="New Booking Alert! 🎉",
            body=f"Your package '{booking.travel_package.package_name}' has been booked by {booking.user.username}.",
        ),
        android=messaging.AndroidConfig(priority="high"),
        apns=messaging.APNSConfig(payload={"aps": {"sound": "default"}}),
    )

    response = None  # Initialize response to avoid UnboundLocalError

    try:
        response = messaging.send(message)
        print(f"✅ FCM Message Sent: {response}")  # Debugging Line
    except Exception as e:
        print(f"❌ FCM Error: {e}")  # Debugging Line
        response = f"Error: {e}"  # Assign a value to response even if there's an error

    # Attempt to create the notification in the database
    try:
        notification = Notification.objects.create(
            travel_agent=travel_agent,
            message=f"Your package '{booking.travel_package.package_name}' has been booked by {booking.user.username}.",
        )
        print(f"✅ Notification Created: {notification}")  # Debugging Line
    except Exception as e:
        print(f"❌ Database Error: {e}")  # Debugging Line

    return response


def get_notifications(request):
    if request.user.is_authenticated and request.user.user_type == "travel_agent":
        try:
            travel_agent_profile = TravelAgentProfile.objects.get(user=request.user)  # Fetch the associated profile
            notifications = Notification.objects.filter(travel_agent=travel_agent_profile, is_read=False).order_by('-timestamp')

            data = [
                {"id": n.id, "message": n.message, "timestamp": n.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
                for n in notifications
            ]
            return JsonResponse({"notifications": data})
        except TravelAgentProfile.DoesNotExist:
            return JsonResponse({"error": "Travel agent profile not found"}, status=404)

    return JsonResponse({"error": "Unauthorized"}, status=403)

# def test_fcm_token_update(request):
#     from travel_agent.views import update_fcm_token
#     response = update_fcm_token(request)
#     return JsonResponse({"message": "FCM Token Update Test", "response": response.content.decode()})

@login_required
def mark_all_read(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        return JsonResponse({"message": "All notifications marked as read."}, status=200)
    
    return JsonResponse({"error": "Invalid request"}, status=400)

# def notification_form(request):
#     return render(request, 'travel_agent/notification.html')

def send_push_notification(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')

        # Custom validation
        if not title or not message:
            messages.error(request, "Both Title and Message are required!")
            return render(request, 'travel_agent/notification.html', {
                'error_messages': ["Both Title and Message are required!"]
            })

        agent_name = request.user.travelagentprofile.travel_company_name

        # Send the FCM Notification
        response = send_fcm_notification_to_users(title, message, agent_name)

        if response.get("error"):
            print("error:",response['error'])
            messages.error(request, f"Failed to send notification: {response['error']}")
        else:
            messages.success(request, "Notification sent successfully to all users!")

        return redirect('send_push_notification')  # Redirect to the notification page

    return render(request, 'travel_agent/notification.html')