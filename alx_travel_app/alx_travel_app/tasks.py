from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_booking_email(user_email, booking_details):
    subject = "Booking Confirmation"
    message = f"Dear User,\n\nYour booking is confirmed:\n{booking_details}"
    send_mail(subject, message, 'your-email@gmail.com', [user_email])
