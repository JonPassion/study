from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from timetable.views import whatsapp_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook/whatsapp/', whatsapp_webhook, name='whatsapp_webhook'),
    path('', lambda request: redirect('admin/')),
]
