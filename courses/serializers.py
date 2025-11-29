from rest_framework import serializers
from .models import Course, CourseMaterial, Announcement

class CourseSerializer(serializers.ModelSerializer):
    """
    课程序列化器
    """
    class Meta:
        model = Course
        fields = '__all__'

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
