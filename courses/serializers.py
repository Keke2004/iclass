from rest_framework import serializers
from .models import Course, CourseMaterial, Announcement, Chapter
from users.serializers import BasicUserSerializer

class ChapterSerializer(serializers.ModelSerializer):
    """
    课程章节序列化器
    """
    class Meta:
        model = Chapter
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    """
    课程序列化器
    """
    teacher = BasicUserSerializer(read_only=True)
    students = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'teacher', 'students', 'description', 'created_at']

class CourseMaterialSerializer(serializers.ModelSerializer):
    """
    课程资料序列化器
    """
    class Meta:
        model = CourseMaterial
        fields = '__all__'

class AnnouncementSerializer(serializers.ModelSerializer):
    """
    课程公告序列化器
    """
    class Meta:
        model = Announcement
        fields = '__all__'
