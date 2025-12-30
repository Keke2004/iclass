from rest_framework import serializers
from .models import Course, CourseMaterial, Announcement, Chapter
from users.serializers import BasicUserSerializer

class ChapterSerializer(serializers.ModelSerializer):
    """
    课程章节序列化器 (动态区分章和节)
    """
    children = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'content', 'course', 'parent', 'children', 'video', 'pdf', 'order', 'created_at']
        read_only_fields = ['course']

    def get_children(self, obj):
        """ 递归地序列化子章节 """
        # 当序列化子章节时，使用同样的 ChapterSerializer
        return ChapterSerializer(obj.children.all(), many=True, context=self.context).data

    def to_representation(self, instance):
        """
        根据是章还是节，动态调整序列化输出
        """
        # 如果是“章” (没有父级)
        if instance.parent is None:
            return {
                'id': instance.id,
                'title': instance.title,
                'order': instance.order,
                'children': self.get_children(instance),
            }
        
        # 如果是“节” (有父级)
        # 使用父类的 to_representation 方法，它会返回 Meta.fields 中定义的所有字段
        representation = super().to_representation(instance)
        # 确保 video 和 pdf 字段返回 URL
        if instance.video:
            representation['video'] = self.context['request'].build_absolute_uri(instance.video.url)
        if instance.pdf:
            representation['pdf'] = self.context['request'].build_absolute_uri(instance.pdf.url)
        return representation


class ChapterWriteSerializer(serializers.ModelSerializer):
    """
    用于创建/更新章节的序列化器，包含验证逻辑
    """
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'content', 'course', 'parent', 'video', 'pdf', 'order']
        read_only_fields = ['course']

    def validate(self, data):
        # 检查是否是章（parent is None）
        # 在创建时，检查 data 中是否有 parent
        # 在更新时，如果 data 中没有 parent，则使用实例的 parent
        is_chapter = data.get('parent') is None
        if self.instance and 'parent' not in data:
            is_chapter = self.instance.parent is None

        if is_chapter:
            # 章不能有内容字段
            has_content = False
            if 'content' in data and data['content'] and data['content'].strip():
                has_content = True
            if 'video' in data and data['video']:
                has_content = True
            if 'pdf' in data and data['pdf']:
                has_content = True

            if has_content:
                raise serializers.ValidationError("章(Chapter)不能包含内容、视频或PDF文件。")
        
        return data

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


class LearningRecordSerializer(serializers.Serializer):
    """
    学习记录序列化器
    """
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    checkin_rate = serializers.FloatField()
    assignment_completion_rate = serializers.FloatField()
    exam_completion_rate = serializers.FloatField()
    discussion_topic_count = serializers.IntegerField()
    discussion_reply_count = serializers.IntegerField()
