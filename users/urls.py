from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserProfileView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('users/profile/', UserProfileView.as_view(), name='user-profile'),
    path('', include(router.urls)),
]
