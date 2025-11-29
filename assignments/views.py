from rest_framework import viewsets
from .models import Assignment, Question, Submission
from .serializers import AssignmentSerializer, QuestionSerializer, SubmissionSerializer

class AssignmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows assignments to be viewed or edited.
    """
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

class QuestionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows questions to be viewed or edited.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class SubmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows submissions to be viewed or edited.
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
