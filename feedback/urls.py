from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionnaireViewSet, FeedbackResponseViewSet

router = DefaultRouter()
router.register(r'questionnaires', QuestionnaireViewSet)
router.register(r'responses', FeedbackResponseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
