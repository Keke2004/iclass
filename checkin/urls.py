from django.urls import path, include
from rest_framework_nested import routers
from .views import CheckinViewSet

# The router is registered in courses/urls.py, so we don't need to register it here.
# This file is for potential future checkin-specific (not course-nested) URLs.
urlpatterns = [
]
