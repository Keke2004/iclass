from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserViewSet, UserProfileView, PasswordChangeView, UserStatisticsView,
    DirectPasswordResetView, MyTokenObtainPairView
)

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('statistics/', UserStatisticsView.as_view(), name='user-statistics'),
    path('auth/password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('auth/password/reset/direct/', DirectPasswordResetView.as_view(), name='direct_password_reset'),
    path('', include(router.urls)),
]
