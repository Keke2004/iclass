from rest_framework import serializers
from .models import DiscussionTopic, DiscussionReply, Attendance, Question, Vote, VoteChoice, VoteResponse, Discussion
from users.serializers import UserSerializer

class DiscussionReplySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = DiscussionReply
        fields = ['id', 'topic', 'content', 'author', 'created_at', 'parent_reply']
        read_only_fields = ['author', 'topic']

class DiscussionTopicSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = DiscussionReplySerializer(many=True, read_only=True)

    class Meta:
        model = DiscussionTopic
        fields = ['id', 'course', 'title', 'content', 'author', 'created_at', 'replies']
        read_only_fields = ['author', 'course']

class AttendanceSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    class Meta:
        model = Attendance
        fields = ['id', 'course', 'student', 'timestamp']

class QuestionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'course', 'student', 'text', 'created_at']

class VoteChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteChoice
        fields = ['id', 'text']

class VoteSerializer(serializers.ModelSerializer):
    choices = VoteChoiceSerializer(many=True, read_only=True)
    class Meta:
        model = Vote
        fields = ['id', 'course', 'title', 'created_at', 'choices']

class VoteResponseSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    class Meta:
        model = VoteResponse
        fields = ['id', 'choice', 'student', 'voted_at']

class DiscussionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    class Meta:
        model = Discussion
        fields = ['id', 'course', 'student', 'message', 'created_at']
