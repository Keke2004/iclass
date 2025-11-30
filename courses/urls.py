from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, CourseMaterialViewSet, AnnouncementViewSet

router = DefaultRouter()
# Register CourseViewSet to the root ('') of the included URL patterns
router.register(r'', CourseViewSet, basename='course')
router.register(r'materials', CourseMaterialViewSet)
router.register(r'announcements', AnnouncementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
