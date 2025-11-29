from rest_framework import serializers
from .models import Questionnaire, FeedbackQuestion, FeedbackResponse, FeedbackAnswer

class FeedbackQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackQuestion
        fields = ['id', 'text', 'question_type']

class QuestionnaireSerializer(serializers.ModelSerializer):
    questions = FeedbackQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Questionnaire
        fields = ['id', 'course', 'title', 'description', 'created_at', 'questions']

class FeedbackAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackAnswer
        fields = ['id', 'question', 'answer_text', 'answer_rating']

class FeedbackResponseSerializer(serializers.ModelSerializer):
    answers = FeedbackAnswerSerializer(many=True)

    class Meta:
        model = FeedbackResponse
        fields = ['id', 'questionnaire', 'student', 'submitted_at', 'answers']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        response = FeedbackResponse.objects.create(**validated_data)
        for answer_data in answers_data:
            FeedbackAnswer.objects.create(response=response, **answer_data)
        return response
