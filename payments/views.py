from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api_keys.authentication import APIKeyAuthentication
from .paystack import PaystackService


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