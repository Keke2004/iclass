from django.urls import path, include
from rest_framework_nested import routers
from .views import CourseViewSet, CourseMaterialViewSet, AnnouncementViewSet, ChapterViewSet, LearningRecordView
from checkin.views import CheckinViewSet

router = routers.DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

courses_router = routers.NestedDefaultRouter(router, r'courses', lookup='course')
courses_router.register(r'chapters', ChapterViewSet, basename='course-chapters')
courses_router.register(r'announcements', AnnouncementViewSet, basename='course-announcements')
courses_router.register(r'materials', CourseMaterialViewSet, basename='course-materials')
courses_router.register(r'checkins', CheckinViewSet, basename='course-checkins')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(courses_router.urls)),
    path('courses/<int:course_id>/learning_records/', LearningRecordView.as_view(), name='learning-records'),
]
