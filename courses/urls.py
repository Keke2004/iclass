from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, CourseMaterialViewSet, AnnouncementViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'materials', CourseMaterialViewSet)
router.register(r'announcements', AnnouncementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
