from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import viewsets

from .models import Booking
from .serializers import BookingSerializer

# Configure Celery with RabbitMQ
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_travel_app.settings")

app = Celery("alx_travel_app")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


# Define the email task
@app.task
def send_booking_confirmation_email(booking_id, user_email):
    subject = "Booking Confirmation"
    message = f"Your booking with ID {booking_id} has been confirmed."
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    send_mail(subject, message, email_from, recipient_list)


# Trigger the email task in BookingViewSet
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        booking = serializer.save()
        # Trigger the email task
        send_booking_confirmation_email.delay(booking.id, booking.user.email)