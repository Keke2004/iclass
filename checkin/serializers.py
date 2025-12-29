from rest_framework import serializers
from .models import Checkin, CheckinRecord
from users.serializers import UserSerializer

class CheckinRecordSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = CheckinRecord
        fields = ('id', 'student', 'checkin_time', 'is_manual')

class CheckinSerializer(serializers.ModelSerializer):
    records = CheckinRecordSerializer(many=True, read_only=True)
    is_checked_in = serializers.SerializerMethodField()

    class Meta:
        model = Checkin
        fields = ('id', 'title', 'start_time', 'end_time', 'is_active', 'records', 'is_checked_in', 'course')
        read_only_fields = ('start_time', 'is_active', 'records', 'course')

    def get_is_checked_in(self, obj):
        """
        检查当前请求的用户是否已经签到
        """
        user = self.context['request'].user
        if user.is_authenticated:
            return CheckinRecord.objects.filter(checkin=obj, student=user).exists()
        return False
