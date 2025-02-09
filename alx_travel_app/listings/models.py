from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Listing(models.Model):
    """
    Listing model for storing properties for a user to book.
    """

    # Fields
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    price_per_night = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationships
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")

    class Meta:
        verbose_name_plural = "Listings"
        verbose_name = "Listing"
        indexes = [
            models.Index(fields=["location"], name="location_idx"),
        ]

    def __str__(self):
        return self.name


class Booking(models.Model):
    """
    Booking model for storing a booking for a property.
    """

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    )

    # Fields
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    # Relationships
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bookings"
    )
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")

    class Meta:
        verbose_name_plural = "Bookings"
        verbose_name = "Booking"

    def __str__(self):
        return f"{self.guest.username} - {self.listing.name}"


class Review(models.Model):
    """
    Review model for storing a review for a property.
    """

    # Fields
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    # Relationships
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")

    class Meta:
        verbose_name_plural = "Reviews"
        verbose_name = "Review"

    def __str__(self):
        return f"{self.user.username} - {self.listing.name}"


class Payment(models.Model):
    PAYMENT_METHODS = (
        ("credit_card", "Credit_card"),
        ("paypal", "PayPal"),
        ("stripe", "Stripe"),
    )
    PAYMENT_STATUS = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    )

    # Fields
    amount = models.DecimalField(max_digits=5, decimal_places=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS, default="pending"
    )
    payment_date = models.DateTimeField(auto_now_add=True)

    # Relationships
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="payments"
    )

    class Meta:
        verbose_name_plural = "Payments"
        verbose_name = "Payment"

    def __str__(self):
        return f"{self.id} - {self.payment_method}"