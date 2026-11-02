from django.urls import path
from .telegram_views import (
    telegram_webhook,
    set_webhook,
    webhook_info,
    delete_webhook
)

urlpatterns = [
    path('webhook/', telegram_webhook, name='telegram-webhook'),
    path('set-webhook/', set_webhook, name='telegram-set-webhook'),
    path('webhook-info/', webhook_info, name='telegram-webhook-info'),
    path('delete-webhook/', delete_webhook, name='telegram-delete-webhook'),
]

