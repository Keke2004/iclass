from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserProfileView, PasswordChangeView, UserStatisticsView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('users/profile/', UserProfileView.as_view(), name='user-profile'),
    path('users/statistics/', UserStatisticsView.as_view(), name='user-statistics'),
    path('auth/password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('', include(router.urls)),
]
