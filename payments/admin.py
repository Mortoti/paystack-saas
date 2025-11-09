from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['reference', 'email', 'amount', 'status', 'channel', 'paid_at', 'created_at']
    list_filter = ['status', 'channel', 'currency', 'created_at']
    search_fields = ['reference', 'email', 'paystack_reference', 'customer_code']
    readonly_fields = ['reference', 'paystack_reference', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        # Prevent manual creation - transactions come from webhooks
        return False