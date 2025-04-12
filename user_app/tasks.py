from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_booking_confirmation_email(user_email, booking_id, package_name, travel_date, total_price):
    subject = 'Booking Confirmation'
    message = (
        f"Dear Traveler,\n\n"
        f"Your booking has been confirmed!\n"
        f"Booking ID: {booking_id}\n"
        f"Package: {package_name}\n"
        f"Travel Date: {travel_date}\n"
        f"Total Price: ${total_price}\n\n"
        f"Thank you for choosing us!\n"
        f"Travel Pro Team"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )