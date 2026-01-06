from rest_framework import serializers
from .models import DiscussionTopic, DiscussionReply, Attendance, Question, Vote, VoteChoice, VoteResponse, Discussion, RandomQuestion
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
    response_count = serializers.IntegerField(source='responses.count', read_only=True)
    voters = serializers.SerializerMethodField()

    class Meta:
        model = VoteChoice
        fields = ['id', 'text', 'response_count', 'voters']

    def get_voters(self, obj):
        user = self.context['request'].user
        # 确保只有课程教师能看到投票的学生列表
        if user.is_authenticated and hasattr(obj.vote.course, 'teacher') and user == obj.vote.course.teacher:
            responses = VoteResponse.objects.filter(choice=obj).select_related('student')
            voters_data = []
            for response in responses:
                student = response.student
                voters_data.append({
                    'id': student.id,
                    'username': student.username
                })
            return voters_data
        return []

class VoteChoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteChoice
        fields = ['text']

class VoteSerializer(serializers.ModelSerializer):
    choices = VoteChoiceSerializer(many=True, read_only=True)
    choices_create = VoteChoiceCreateSerializer(many=True, write_only=True)
    user_has_voted = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()
    start_time = serializers.DateTimeField(source='created_at', read_only=True)
    task_type = serializers.SerializerMethodField()

    class Meta:
        model = Vote
        fields = ['id', 'course', 'title', 'created_at', 'is_active', 'choices', 'choices_create', 'user_has_voted', 'total_votes', 'start_time', 'task_type']
        read_only_fields = ['course']

    def get_task_type(self, obj):
        return 'vote'

    def get_user_has_voted(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False

        # 如果用户是该课程的老师，则始终认为“已投票”，以显示结果
        if hasattr(obj.course, 'teacher') and user == obj.course.teacher:
            return True

        # 对于学生，检查他们是否真的投过票
        return obj.responses.filter(student=user).exists()

    def get_total_votes(self, obj):
        return obj.responses.count()

    def create(self, validated_data):
        choices_data = validated_data.pop('choices_create')
        vote = Vote.objects.create(**validated_data)
        for choice_data in choices_data:
            VoteChoice.objects.create(vote=vote, **choice_data)
        return vote

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


class RandomQuestionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    task_type = serializers.SerializerMethodField()
    start_time = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = RandomQuestion
        fields = ('id', 'course', 'student', 'created_at', 'task_type', 'start_time', 'status')
        read_only_fields = ('course', 'student', 'created_at')

    def get_task_type(self, obj):
        return 'random_question'


class RandomQuestionDetailSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = RandomQuestion
        fields = ['id', 'course', 'student', 'created_at', 'status']
