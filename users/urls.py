from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserProfileView, PasswordChangeView, UserStatisticsView,
    DirectPasswordResetView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('users/profile/', UserProfileView.as_view(), name='user-profile'),
    path('users/statistics/', UserStatisticsView.as_view(), name='user-statistics'),
    path('auth/password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('auth/password/reset/direct/', DirectPasswordResetView.as_view(), name='direct_password_reset'),
    path('', include(router.urls)),
]
