from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionnaireViewSet, FeedbackResponseViewSet

router = DefaultRouter()
router.register(r'questionnaires', QuestionnaireViewSet)
router.register(r'feedback/responses', FeedbackResponseViewSet, basename='feedback-responses')

urlpatterns = [
    path('', include(router.urls)),
]
