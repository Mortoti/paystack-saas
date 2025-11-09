from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api_keys.authentication import APIKeyAuthentication
from .paystack import PaystackService
import hashlib
import hmac
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import Transaction
from datetime import datetime


class InitializePaymentView(APIView):
    authentication_classes = [APIKeyAuthentication]

    def post(self, request):
        """Initialize a payment transaction"""
        email = request.data.get('email')
        amount = request.data.get('amount')
        reference = request.data.get('reference')
        callback_url = request.data.get('callback_url')

        if not email or not amount:
            return Response(
                {'error': 'Email and amount are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            paystack = PaystackService()
            result = paystack.initialize_transaction(
                email=email,
                amount=float(amount),
                reference=reference,
                callback_url=callback_url
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyPaymentView(APIView):
    authentication_classes = [APIKeyAuthentication]

    def get(self, request, reference):
        """Verify a payment transaction"""
        try:
            paystack = PaystackService()
            result = paystack.verify_transaction(reference)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListTransactionsView(APIView):
    authentication_classes = [APIKeyAuthentication]

    def get(self, request):
        """List all transactions"""
        page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 50)

        try:
            paystack = PaystackService()
            result = paystack.list_transactions(page=int(page), per_page=int(per_page))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class PaystackWebhookView(APIView):
    authentication_classes = []  # Webhooks don't use API key auth

    def post(self, request):
        """Handle Paystack webhook notifications"""

        # Get the signature from headers
        paystack_signature = request.headers.get('X-Paystack-Signature')

        if not paystack_signature:
            return Response(
                {'error': 'No signature provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify the webhook signature
        secret_key = config('PAYSTACK_SECRET_KEY', default='')

        # Create hash of the request body
        hash_object = hmac.new(
            secret_key.encode('utf-8'),
            request.body,
            hashlib.sha512
        )
        expected_signature = hash_object.hexdigest()

        # Compare signatures
        if paystack_signature != expected_signature:
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Process the webhook event
        event = request.data.get('event')
        data = request.data.get('data', {})

        if event == 'charge.success':
            # Payment was successful
            self.handle_successful_payment(data)
        elif event == 'charge.failed':
            # Payment failed
            self.handle_failed_payment(data)

        return Response({'status': 'success'}, status=status.HTTP_200_OK)

    def handle_successful_payment(self, data):
        """Handle successful payment webhook"""
        reference = data.get('reference')

        # Create or update transaction
        transaction, created = Transaction.objects.update_or_create(
            reference=reference,
            defaults={
                'email': data.get('customer', {}).get('email', ''),
                'amount': data.get('amount', 0) / 100,  # Convert from kobo to cedis
                'status': 'success',
                'paystack_reference': data.get('id', ''),
                'paid_at': datetime.fromisoformat(data.get('paid_at', '').replace('Z', '+00:00')) if data.get(
                    'paid_at') else None,
                'channel': data.get('channel', ''),
                'currency': data.get('currency', 'GHS'),
                'customer_code': data.get('customer', {}).get('customer_code', ''),
                'metadata': data.get('metadata', {}),
            }
        )

        return transaction

    def handle_failed_payment(self, data):
        """Handle failed payment webhook"""
        reference = data.get('reference')

        transaction, created = Transaction.objects.update_or_create(
            reference=reference,
            defaults={
                'email': data.get('customer', {}).get('email', ''),
                'amount': data.get('amount', 0) / 100,
                'status': 'failed',
                'paystack_reference': data.get('id', ''),
                'channel': data.get('channel', ''),
                'currency': data.get('currency', 'GHS'),
                'customer_code': data.get('customer', {}).get('customer_code', ''),
                'metadata': data.get('metadata', {}),
            }
        )

        return transaction