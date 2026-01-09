from rest_framework import serializers
from .models import Questionnaire, FeedbackQuestion, FeedbackResponse, FeedbackAnswer
from users.serializers import BasicUserSerializer

class FeedbackQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackQuestion
        fields = ['id', 'text', 'question_type']

class FeedbackAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackAnswer
        fields = ['id', 'question', 'answer_text', 'answer_rating']

class FeedbackResponseSerializer(serializers.ModelSerializer):
    answers = FeedbackAnswerSerializer(many=True)
    student = BasicUserSerializer(read_only=True)

    class Meta:
        model = FeedbackResponse
        fields = ['id', 'questionnaire', 'student', 'submitted_at', 'answers']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        response = FeedbackResponse.objects.create(**validated_data)
        for answer_data in answers_data:
            FeedbackAnswer.objects.create(response=response, **answer_data)
        return response

class QuestionnaireSerializer(serializers.ModelSerializer):
    questions = FeedbackQuestionSerializer(many=True)
    student_statuses = serializers.SerializerMethodField()

    class Meta:
        model = Questionnaire
        fields = ['id', 'course', 'title', 'created_at', 'questions', 'student_statuses']

    def get_student_statuses(self, obj):
        course = obj.course
        students = course.students.all()
        questionnaire_id = obj.id

        statuses = []
        for student in students:
            response = FeedbackResponse.objects.filter(questionnaire_id=questionnaire_id, student=student).first()
            if response:
                statuses.append({
                    'student': BasicUserSerializer(student).data,
                    'status': 'submitted',
                    'response': FeedbackResponseSerializer(response).data
                })
            else:
                statuses.append({
                    'student': BasicUserSerializer(student).data,
                    'status': 'not_submitted',
                    'response': None
                })
        return statuses

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        questionnaire = Questionnaire.objects.create(**validated_data)
        for question_data in questions_data:
            FeedbackQuestion.objects.create(questionnaire=questionnaire, **question_data)
        return questionnaire

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions')
        instance.title = validated_data.get('title', instance.title)
        instance.save()

        # Clear existing responses
        instance.responses.all().delete()

        # Simple update logic: clear existing questions and add new ones
        instance.questions.all().delete()
        for question_data in questions_data:
            FeedbackQuestion.objects.create(questionnaire=instance, **question_data)

        return instance
