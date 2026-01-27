from rest_framework import serializers
from .models import Notification
from users.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    related_object_info = serializers.SerializerMethodField()
    content_type_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ('id', 'sender', 'message', 'timestamp', 'is_read', 'content_type', 'object_id', 'related_object_info', 'content_type_name')

    def get_content_type_name(self, obj):
        return obj.content_type.model

    def get_related_object_info(self, obj):
        """
        返回关联对象的序列化表示。
        """
        related_object = obj.related_object
        if not related_object:
            return None

        # 根据模型类型动态选择序列化器或手动构建字典
        model_name = obj.content_type.model
        if model_name in ['assignment', 'exam', 'discussiontopic', 'announcement', 'vote', 'checkin', 'question', 'randomquestion']:
            # 这些模型都有 course 字段
            return {
                'course_id': related_object.course.id,
                'id': related_object.id
            }
        elif hasattr(related_object, 'course_id'):
             return {
                'course_id': related_object.course.id,
                'id': related_object.id
            }
        elif model_name == 'voteresponse':
            return {
                'course_id': related_object.vote.course.id,
                'id': related_object.vote.id
            }
        elif model_name == 'checkinrecord':
            return {
                'course_id': related_object.checkin.course.id,
                'id': related_object.checkin.id
            }
        elif model_name == 'submission':
            return {
                'course_id': related_object.assignment.course.id,
                'id': related_object.assignment.id
            }
        elif model_name == 'examsubmission':
            return {
                'course_id': related_object.exam.course.id,
                'id': related_object.exam.id
            }
        elif model_name == 'discussionreply':
            return {
                'course_id': related_object.topic.course.id,
                'id': related_object.topic.id
            }
        elif model_name == 'feedbackresponse':
            return {
                'course_id': related_object.questionnaire.course.id,
                'id': related_object.questionnaire.id
            }
        elif model_name == 'feedback':
            return {
                'course_id': related_object.course.id,
                'id': related_object.id
            }
        # 可以为其他没有 course 字段的模型添加更多逻辑
        # 例如，用户相关的通知可能不需要 course_id
        return None
