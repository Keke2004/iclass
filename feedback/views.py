from rest_framework import viewsets
from .models import Questionnaire, FeedbackResponse
from .serializers import QuestionnaireSerializer, FeedbackResponseSerializer

class QuestionnaireViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows questionnaires to be viewed or edited.
    """
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer

class FeedbackResponseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows feedback responses to be viewed or edited.
    """
    queryset = FeedbackResponse.objects.all()
    serializer_class = FeedbackResponseSerializer
