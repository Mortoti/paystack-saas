from django.db import models
from django.contrib.auth.models import User
import secrets


class APIKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    key = models.CharField(max_length=64, unique=True, editable=False)
    name = models.CharField(max_length=100, help_text="A name to identify this API key")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        return f"pk_{''.join(secrets.token_hex(32))}"

    def __str__(self):
        return f"{self.name} - {self.key[:20]}..."

    class Meta:
        ordering = ['-created_at']