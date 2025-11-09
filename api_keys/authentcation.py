from rest_framework import authentication
from rest_framework import exceptions
from .models import APIKey
from django.utils import timezone


class APIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return None

        try:
            key_obj = APIKey.objects.get(key=api_key, is_active=True)
            # Update last used timestamp
            key_obj.last_used = timezone.now()
            key_obj.save(update_fields=['last_used'])
            return (key_obj.user, key_obj)
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API key')