from django.urls import path
from .views import InitializePaymentView, VerifyPaymentView, ListTransactionsView

urlpatterns = [
    path('initialize/', InitializePaymentView.as_view(), name='initialize-payment'),
    path('verify/<str:reference>/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('transactions/', ListTransactionsView.as_view(), name='list-transactions'),
]