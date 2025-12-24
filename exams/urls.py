from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamViewSet, ExamSubmissionViewSet, SubmissionsForExamView

router = DefaultRouter()
router.register(r'exams', ExamViewSet)
router.register(r'exam-submissions', ExamSubmissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('exams/<int:exam_id>/submissions/', SubmissionsForExamView.as_view(), name='exam-submissions-list'),
]
