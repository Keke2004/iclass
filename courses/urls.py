from django.urls import path, include
from rest_framework_nested import routers
from .views import CourseViewSet, CourseMaterialViewSet, AnnouncementViewSet, ChapterViewSet

router = routers.DefaultRouter()
router.register(r'', CourseViewSet, basename='course')

courses_router = routers.NestedDefaultRouter(router, r'', lookup='course_pk')
courses_router.register(r'chapters', ChapterViewSet, basename='course-chapters')
courses_router.register(r'announcements', AnnouncementViewSet, basename='course-announcements')
courses_router.register(r'materials', CourseMaterialViewSet, basename='course-materials')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(courses_router.urls)),
]
