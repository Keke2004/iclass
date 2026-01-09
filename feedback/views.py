from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Questionnaire, FeedbackResponse, FeedbackAnswer
from .serializers import QuestionnaireSerializer, FeedbackResponseSerializer
from courses.permissions import IsTeacherOrReadOnly

class QuestionnaireViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows questionnaires to be viewed or edited.
    """
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]

    def get_queryset(self):
        if self.action == 'list':
            course_id = self.request.query_params.get('course_id')
            if course_id:
                return self.queryset.filter(course_id=course_id)
            return self.queryset.none()
        return self.queryset

    def perform_create(self, serializer):
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Check if the user has already submitted a response
        user = request.user
        response_data = serializer.data
        
        if user.is_authenticated:
            feedback_response = FeedbackResponse.objects.filter(questionnaire=instance, student=user).first()
            if feedback_response:
                answers = FeedbackAnswer.objects.filter(response=feedback_response)
                # We need a serializer for FeedbackAnswer, let's assume it exists and is named FeedbackAnswerSerializer
                # from .serializers import FeedbackAnswerSerializer
                # For now, let's just pass the raw data
                response_data['user_response'] = {
                    'response_id': feedback_response.id,
                    'answers': list(answers.values('question', 'answer_text', 'answer_rating'))
                }

        return Response(response_data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def results(self, request, pk=None):
        questionnaire = self.get_object()
        # Simple result aggregation
        results = {}
        for question in questionnaire.questions.all():
            answers = FeedbackAnswer.objects.filter(question=question)
            if question.question_type == 'rating':
                ratings = [a.answer_rating for a in answers if a.answer_rating is not None]
                results[question.id] = {
                    'text': question.text,
                    'type': 'rating',
                    'average': sum(ratings) / len(ratings) if ratings else 0,
                    'count': len(ratings)
                }
            else:
                texts = [a.answer_text for a in answers if a.answer_text]
                results[question.id] = {
                    'text': question.text,
                    'type': 'text',
                    'answers': texts
                }
        return Response(results)


class FeedbackResponseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows feedback responses to be viewed or edited.
    """
    queryset = FeedbackResponse.objects.all()
    serializer_class = FeedbackResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(student=user)

    def perform_create(self, serializer):
        questionnaire_id = self.request.data.get('questionnaire')
        if FeedbackResponse.objects.filter(questionnaire_id=questionnaire_id, student=self.request.user).exists():
            raise status.HTTP_400_BAD_REQUEST
        serializer.save(student=self.request.user)
