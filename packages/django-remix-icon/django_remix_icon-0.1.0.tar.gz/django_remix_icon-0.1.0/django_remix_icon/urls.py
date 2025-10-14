"""
URL configuration for django-remix-icon.
"""

from django.urls import path
from django_remix_icon import views

app_name = 'django_remix_icon'

urlpatterns = [
    path('search/', views.IconSearchView.as_view(), name='icon_search'),
    path('list/', views.icon_list_view, name='icon_list'),
]
