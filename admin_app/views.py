from django.http import JsonResponse
from django.shortcuts import render, redirect
from common.models import CustomUser
from user_app.models import *
from travel_agent.models import *
from django.db.models import Count, Avg, Q, Sum
from datetime import date
from . models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

# Create your views here.
def admin_dashboard(request):
    context = {
        'notifications': get_notifications(),
    }
    return render(request, 'admin_app/admin_dashboard.html', context)

def customer_management(request):
    # Fetch customers (users with user_type='user')
    customers = CustomUser.objects.filter(user_type='user').select_related('profile')

    search_query = request.GET.get('search', '')

    # Apply search filter if query exists
    if search_query:
        customers = customers.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Prepare customer data with additional details
    customer_data = []
    for customer in customers:
        # Get booking stats
        bookings = Booking.objects.filter(user=customer)
        total_bookings = bookings.count()
        
        # Get last booking date
        last_booking = bookings.order_by('-booking_date').first()
        last_booking_date = last_booking.booking_date if last_booking else None
        
        # Get preferred destinations (based on bookings)
        destinations = bookings.values('travel_package__destination').distinct()
        preferred_destinations = [d['travel_package__destination'] for d in destinations]
        
        customer_data.append({
            'id': customer.id,
            'name': customer.username,
            'email': customer.email,
            'phone': customer.phone,
            'status': 'Active' if customer.is_active else 'Blocked',
            'total_bookings': total_bookings,
            'last_booking_date': last_booking_date,
            'preferred_destinations': preferred_destinations,
        })
    
    context = {
        'customers': customer_data,
        'search_query': search_query,
    }
    return render(request, 'admin_app/customer-management.html', context)

def agent_management(request):
    # Get search query from request
    search_query = request.GET.get('search', '')
    
    # Fetch travel agents (users with user_type='travel_agent')
    agents = CustomUser.objects.filter(
        user_type='travel_agent'
    ).select_related('travelagentprofile')
    
    # Apply search filter if query exists
    if search_query:
        agents = agents.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(travelagentprofile__travel_company_name__icontains=search_query)
        )
    
    # Prepare agent data with additional details
    agent_data = []
    for agent in agents:
        # Get profile
        profile = agent.travelagentprofile if hasattr(agent, 'travelagentprofile') else None
        
        # Get package and booking stats
        packages = TravelPackage.objects.filter(travel_agent=agent)
        total_packages = packages.count()
        
        bookings = Booking.objects.filter(travel_package__travel_agent=agent)
        total_bookings = bookings.count()
        
        # Get last booking date
        last_booking = bookings.order_by('-booking_date').first()
        last_booking_date = last_booking.booking_date if last_booking else None
        
        agent_data.append({
            'id': agent.id,
            'name': agent.username,
            'email': agent.email,
            'phone': agent.phone,
            'business_name': profile.travel_company_name if profile else 'N/A',
            'status': 'Active' if agent.is_active else 'Inactive',
            'total_packages': total_packages,
            'total_bookings': total_bookings,
            'last_booking_date': last_booking_date,
            'is_pro': profile.is_pro if profile else False,
            'pro_expiry_date': profile.pro_expiry_date if profile else None,
        })
    
    context = {
        'agents': agent_data,
        'search_query': search_query,
    }
    return render(request, 'admin_app/agent_management.html', context)


def toggle_agent_status(request):
    agent_id = request.POST.get('agent_id')
    try:
        agent = CustomUser.objects.get(id=agent_id, user_type='travel_agent')
        agent.is_active = not agent.is_active
        agent.save()
        return JsonResponse({
            'success': True,
            'new_status': 'Active' if agent.is_active else 'Inactive'
        })
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)


def mark_notification_read(request, notification_id):
    try:
        notification = AdminNotification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))
    except AdminNotification.DoesNotExist:
        messages.error(request, "Notification not found.")
        return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

def get_notifications():
    """Helper function to prepare notifications with complaint details."""
    notifications = AdminNotification.objects.filter(is_read=False).order_by('-timestamp')
    notification_data = []
    for notification in notifications:
        data = {
            'id': notification.id,
            'type': notification.type,
            'type_display': notification.get_type_display(),
            'message': notification.message,
            'timestamp': notification.timestamp,
            'is_read': notification.is_read,
            'complaint_details': None,
        }
        if notification.type == 'complaint' and notification.related_id:
            try:
                complaint = Complaint.objects.get(id=notification.related_id)
                data['complaint_details'] = {
                    'subject': complaint.subject,
                    'name': complaint.name,
                    'email': complaint.email,
                    'file_url': complaint.file.url if complaint.file else None,
                }
            except Complaint.DoesNotExist:
                pass  # Skip if complaint is deleted
        notification_data.append(data)
    return notification_data

def complaint_view(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    return render(request, 'admin_app/complaint_view.html', {'complaints': complaints})

def send_message(request):
    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        print(complaint_id)
        message_text = request.POST.get('message')
        
        print(f"send_message: complaint_id={complaint_id}, message={message_text}")
        
        if not message_text:
            print("Validation failed: Message is empty")
            messages.error(request, "Message cannot be empty.")
            return redirect('complaint_view')
        
        try:
            # complaint = Complaint.objects.get(id=complaint_id)
            AdminNotification.objects.create(
                type='general',
                message=message_text,
                related_id=complaint_id,
                is_read=False
            )
            print(f"Message saved for complaint {complaint_id}")
            messages.success(request, "Message sent successfully.")
        except Complaint.DoesNotExist:
            print(f"Complaint {complaint_id} not found")
            messages.error(request, "Complaint not found.")
        
        return redirect('complaint_view')
    
    print("Invalid request method")
    messages.error(request, "Invalid request.")
    return redirect('complaint_view')


def commission_report(request):
        
    # Fetch commissions for the logged-in admin
    commissions = Commission.objects.all().order_by('-created_at')

    # Aggregate totals
    commission_summary = commissions.aggregate(
        total=Sum('amount'),
        booking_total=Sum('amount', filter=Q(source='booking')),
        pro_upgrade_total=Sum('amount', filter=Q(source='pro_upgrade'))
    )

    context = {
        'commissions': commissions,
        'summary': {
            'total': commission_summary['total'] or 0,
            'booking_total': commission_summary['booking_total'] or 0,
            'pro_upgrade_total': commission_summary['pro_upgrade_total'] or 0,
        }
    }

    return render(request, 'admin_app/commission_report.html', context)