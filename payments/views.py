from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .paystack import PaystackService
from .models import Transaction
from api_keys.models import APIKey
import hmac
import hashlib
from decouple import config


class InitializePaymentView(APIView):
    @swagger_auto_schema(
        operation_description="Initialize a new payment transaction with Paystack",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'amount'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Customer email address',
                    example='customer@example.com'
                ),
                'amount': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Amount in pesewas (GHS) or smallest currency unit',
                    example=50000
                ),
                'currency': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Currency code',
                    default='GHS',
                    example='GHS'
                ),
                'reference': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Unique transaction reference (optional)',
                    example='TXN_123456'
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Payment initialized successfully",
                examples={
                    "application/json": {
                        "status": True,
                        "message": "Authorization URL created",
                        "data": {
                            "authorization_url": "https://checkout.paystack.com/xxx",
                            "access_code": "xxx",
                            "reference": "xxx"
                        }
                    }
                }
            ),
            400: "Bad Request - Missing or invalid data",
            401: "Unauthorized - Invalid API key"
        }
    )
    def post(self, request):
        # Get API key from header
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return Response(
                {'error': 'API key is required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Validate API key
        try:
            api_key_obj = APIKey.objects.get(key=api_key, is_active=True)
        except APIKey.DoesNotExist:
            return Response(
                {'error': 'Invalid API key'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Get payment data
        email = request.data.get('email')
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'GHS')
        reference = request.data.get('reference')

        if not email or not amount:
            return Response(
                {'error': 'Email and amount are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Initialize payment with Paystack
        paystack = PaystackService()
        result = paystack.initialize_transaction(
            email=email,
            amount=amount,
            currency=currency,
            reference=reference
        )

        if result.get('status'):
            # Save transaction to database
            Transaction.objects.create(
                api_key=api_key_obj,
                reference=result['data']['reference'],
                amount=amount,
                currency=currency,
                email=email,
                status='pending'
            )

            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class VerifyPaymentView(APIView):
    @swagger_auto_schema(
        operation_description="Verify the status of a payment transaction",
        responses={
            200: openapi.Response(
                description="Payment verification successful",
                examples={
                    "application/json": {
                        "status": True,
                        "message": "Verification successful",
                        "data": {
                            "id": 123456,
                            "status": "success",
                            "reference": "TXN_123456",
                            "amount": 50000,
                            "currency": "GHS",
                            "paid_at": "2024-01-01T12:00:00.000Z",
                            "customer": {
                                "email": "customer@example.com"
                            }
                        }
                    }
                }
            ),
            404: "Transaction not found",
            401: "Unauthorized - Invalid API key"
        }
    )
    def get(self, request, reference):
        # Get API key from header
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return Response(
                {'error': 'API key is required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Validate API key
        try:
            api_key_obj = APIKey.objects.get(key=api_key, is_active=True)
        except APIKey.DoesNotExist:
            return Response(
                {'error': 'Invalid API key'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Verify payment with Paystack
        paystack = PaystackService()
        result = paystack.verify_transaction(reference)

        if result.get('status'):
            # Update transaction in database
            try:
                transaction = Transaction.objects.get(reference=reference)
                transaction.status = result['data']['status']
                transaction.save()
            except Transaction.DoesNotExist:
                pass

            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)


class ListTransactionsView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all payment transactions",
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number for pagination",
                type=openapi.TYPE_INTEGER,
                required=False,
                default=1
            ),
            openapi.Parameter(
                'perPage',
                openapi.IN_QUERY,
                description="Number of items per page",
                type=openapi.TYPE_INTEGER,
                required=False,
                default=50
            )
        ],
        responses={
            200: openapi.Response(
                description="List of transactions retrieved successfully",
                examples={
                    "application/json": {
                        "status": True,
                        "message": "Transactions retrieved",
                        "data": [
                            {
                                "id": 123456,
                                "reference": "TXN_123456",
                                "amount": 50000,
                                "currency": "GHS",
                                "status": "success",
                                "paid_at": "2024-01-01T12:00:00.000Z"
                            }
                        ]
                    }
                }
            ),
            401: "Unauthorized - Invalid API key"
        }
    )
    def get(self, request):
        # Get API key from header
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return Response(
                {'error': 'API key is required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Validate API key
        try:
            api_key_obj = APIKey.objects.get(key=api_key, is_active=True)
        except APIKey.DoesNotExist:
            return Response(
                {'error': 'Invalid API key'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Get pagination parameters
        page = request.GET.get('page', 1)
        per_page = request.GET.get('perPage', 50)

        # Get transactions from Paystack
        paystack = PaystackService()
        result = paystack.list_transactions(page=page, per_page=per_page)

        return Response(result, status=status.HTTP_200_OK)


class PaystackWebhookView(APIView):
    @swagger_auto_schema(
        operation_description="Receive webhook notifications from Paystack for payment events",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'event': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Event type',
                    example='charge.success'
                ),
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description='Event payload data'
                ),
            },
        ),
        responses={
            200: "Webhook processed successfully",
            400: "Invalid signature or bad request"
        }
    )
    def post(self, request):
        # Verify webhook signature
        paystack_signature = request.headers.get('X-Paystack-Signature')

        if not paystack_signature:
            return Response(
                {'error': 'No signature found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Compute signature
        secret = config('PAYSTACK_SECRET_KEY')
        hash_value = hmac.new(
            secret.encode('utf-8'),
            request.body,
            hashlib.sha512
        ).hexdigest()

        if hash_value != paystack_signature:
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Process webhook event
        event = request.data.get('event')
        data = request.data.get('data')

        if event == 'charge.success':
            # Update transaction status
            reference = data.get('reference')
            try:
                transaction = Transaction.objects.get(reference=reference)
                transaction.status = 'success'
                transaction.save()
            except Transaction.DoesNotExist:
                pass

        return Response({'status': 'success'}, status=status.HTTP_200_OK)