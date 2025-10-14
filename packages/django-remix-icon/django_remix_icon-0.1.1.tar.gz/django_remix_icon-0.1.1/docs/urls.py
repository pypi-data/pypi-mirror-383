"""
URL configuration for documentation.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('remix-icon/', include('django_remix_icon.urls')),
]
