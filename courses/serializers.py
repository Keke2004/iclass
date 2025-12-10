from rest_framework import serializers
from .models import Course, CourseMaterial, Announcement, Chapter
from users.serializers import BasicUserSerializer

class ChapterSerializer(serializers.ModelSerializer):
    """
    课程章节序列化器
    """
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'content', 'course', 'created_at']
        read_only_fields = ['course']

class CourseSerializer(serializers.ModelSerializer):
    """
    课程序列化器
    """
    teacher = BasicUserSerializer(read_only=True)
    students = BasicUserSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'teacher', 'students', 'description', 'created_at']


class CourseListSerializer(CourseSerializer):
    """
    用于课程列表的轻量级序列化器
    """
    students = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

class CourseMaterialSerializer(serializers.ModelSerializer):
    """
    课程资料序列化器
    """
    uploaded_by = BasicUserSerializer(read_only=True)

    class Meta:
        model = CourseMaterial
        fields = ['id', 'name', 'file', 'size', 'uploaded_by', 'uploaded_at', 'course']
        read_only_fields = ['course', 'size', 'uploaded_by']

class AnnouncementSerializer(serializers.ModelSerializer):
    """
    课程公告序列化器
    """
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'course', 'created_at']
        read_only_fields = ['course']
