import requests
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, Listing, Payment, Review
from .serializers import BookingSerializer, ListingSerializer, ReviewSerializer


class ListingsViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingsViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class PaymentView(APIView):
    def post(self, request):
        # Payment initiation logic
        booking_reference = request.data.get("booking_reference")
        amount = request.data.get("amount")

        if not booking_reference or not amount:
            return Response(
                {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        payment = Payment.objects.create(
            booking_reference=booking_reference, amount=amount
        )

        headers = self._get_chapa_headers("application/json")
        payload = {
            "amount": str(amount),
            "currency": "ETB",
            "email": request.data.get("email"),
            "tx_ref": str(payment.transaction_id),
            "return_url": "https://yourwebsite.com/payment-success/",
            "callback_url": "https://yourwebsite.com/api/payments/verify/",
        }

        response = requests.post(settings.CHAPA_URL, json=payload, headers=headers)

        try:
            chapa_response = response.json()
        except requests.exceptions.JSONDecodeError:
            return Response(
                {"error": "Invalid response from Chapa", "details": response.text},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if response.status_code == 200 and chapa_response.get("status") == "success":
            return Response(
                {"payment_url": chapa_response["data"]["checkout_url"]},
                status=status.HTTP_200_OK,
            )
        else:
            payment.status = "Failed"
            payment.save()
            return Response(
                {
                    "error": "Payment initiation failed",
                    "chapa_response": chapa_response,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get(self, request):
        # Payment verification logic
        transaction_id = request.GET.get("transaction_id")
        if not transaction_id:
            return Response(
                {"error": "Missing transaction ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        payment = Payment.objects.filter(transaction_id=transaction_id).first()
        if not payment:
            return Response(
                {"error": "Invalid transaction ID"}, status=status.HTTP_404_NOT_FOUND
            )

        headers = self._get_chapa_headers()
        verify_url = f"https://api.chapa.co/v1/transaction/verify/{transaction_id}"
        response = requests.get(verify_url, headers=headers)

        try:
            chapa_response = response.json()
        except requests.exceptions.JSONDecodeError:
            return Response(
                {"error": "Invalid verification response", "details": response.text},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if chapa_response.get("status") == "success":
            payment.status = "Completed"
            payment.save()
            return Response(
                {"message": "Payment verified successfully", "status": payment.status},
                status=status.HTTP_200_OK,
            )
        else:
            payment.status = "Failed"
            payment.save()
            return Response(
                {"message": "Payment verification failed", "status": payment.status},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _get_chapa_headers(self, content_type=None):
        # Helper method for Chapa headers
        headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
        if content_type:
            headers["Content-Type"] = content_type
        return headers