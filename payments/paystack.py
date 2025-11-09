import requests
from django.conf import settings
from decouple import config


class PaystackService:
    BASE_URL = "https://api.paystack.co"

    def __init__(self):
        self.secret_key = config('PAYSTACK_SECRET_KEY', default='')
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }

    def initialize_transaction(self, email, amount, reference=None, callback_url=None):
        """Initialize a Paystack transaction"""
        url = f"{self.BASE_URL}/transaction/initialize"

        data = {
            "email": email,
            "amount": int(amount * 100)  # Convert to kobo/cents
        }

        if reference:
            data['reference'] = reference
        if callback_url:
            data['callback_url'] = callback_url

        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def verify_transaction(self, reference):
        """Verify a Paystack transaction"""
        url = f"{self.BASE_URL}/transaction/verify/{reference}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def list_transactions(self, page=1, per_page=50):
        """List all transactions"""
        url = f"{self.BASE_URL}/transaction?page={page}&perPage={per_page}"
        response = requests.get(url, headers=self.headers)
        return response.json()