from rest_framework import serializers
from django.db import models
from .models import Course, CourseMaterial, Announcement, Chapter, ChapterReadStatus
from users.serializers import BasicUserSerializer

class ChapterSerializer(serializers.ModelSerializer):
    """
    课程章节序列化器 (动态区分章和节)
    """
    children = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'content', 'course', 'parent', 'children', 'video', 'pdf', 'order', 'created_at', 'is_read']
        read_only_fields = ['course']

    def get_children(self, obj):
        """ 递归地序列化子章节 """
        # 当序列化子章节时，使用同样的 ChapterSerializer
        return ChapterSerializer(obj.children.all(), many=True, context=self.context).data

    def get_is_read(self, obj):
        """ 检查当前用户是否已读此章节 """
        user = self.context['request'].user
        if user.is_authenticated:
            # 章（parent is None）不应该有已读状态，始终返回 False
            if obj.parent is None:
                return False
            # 对于节，直接检查已读状态
            else:
                return ChapterReadStatus.objects.filter(user=user, chapter=obj).exists()
        return False

    def to_representation(self, instance):
        """
        根据是章还是节，动态调整序列化输出
        """
        is_read = self.get_is_read(instance)
        # 如果是“章” (没有父级)
        if instance.parent is None:
            return {
                'id': instance.id,
                'title': instance.title,
                'order': instance.order,
                'children': self.get_children(instance),
                'is_read': is_read,
            }
        
        # 如果是“节” (有父级)
        # 使用父类的 to_representation 方法，它会返回 Meta.fields 中定义的所有字段
        representation = super().to_representation(instance)
        representation['is_read'] = is_read
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
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'teacher', 'students', 'cover', 'created_at', 'progress']

    def get_progress(self, obj):
        """
        计算课程的任务点完成进度
        """
        user = self.context['request'].user
        if not user.is_authenticated:
            return {'completed': 0, 'total': 0}

        # 任务点被定义为没有子节点的章节（即“节”）
        task_points = Chapter.objects.filter(course=obj, children__isnull=True)
        total_tasks = task_points.count()

        if total_tasks == 0:
            return {'completed': 0, 'total': 0}

        completed_tasks = ChapterReadStatus.objects.filter(
            user=user,
            chapter__in=task_points
        ).count()

        return {'completed': completed_tasks, 'total': total_tasks}


class CourseListSerializer(CourseSerializer):
    """
    用于课程列表的轻量级序列化器
    """
    students = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['progress']

    def get_progress(self, obj):
        """
        计算课程的任务点完成进度
        """
        user = self.context['request'].user
        if not user.is_authenticated:
            return {'completed': 0, 'total': 0}

        # 任务点被定义为没有子节点的章节（即“节”）
        task_points = Chapter.objects.filter(course=obj, children__isnull=True)
        total_tasks = task_points.count()

        if total_tasks == 0:
            return {'completed': 0, 'total': 0}

        completed_tasks = ChapterReadStatus.objects.filter(
            user=user,
            chapter__in=task_points
        ).count()

        return {'completed': completed_tasks, 'total': total_tasks}

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


class CheckinSummarySerializer(serializers.Serializer):
    total = serializers.IntegerField()
    present = serializers.IntegerField()
    late = serializers.IntegerField()
    absent = serializers.IntegerField()
    sick_leave = serializers.IntegerField()
    personal_leave = serializers.IntegerField()
    attendance_rate = serializers.FloatField()

class TaskSummarySerializer(serializers.Serializer):
    total = serializers.IntegerField()
    completed = serializers.IntegerField()
    completion_rate = serializers.FloatField()

class DiscussionSummarySerializer(serializers.Serializer):
    topic_count = serializers.IntegerField()
    reply_count = serializers.IntegerField()

class LearningRecordSerializer(serializers.Serializer):
    """
    学习记录序列化器
    """
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    checkin_summary = CheckinSummarySerializer()
    assignment_summary = TaskSummarySerializer()
    exam_summary = TaskSummarySerializer()
    discussion_summary = DiscussionSummarySerializer()
    chapter_summary = serializers.SerializerMethodField()

    def get_chapter_summary(self, obj):
        """
        计算章节任务点的完成进度
        """
        course = self.context.get('course')
        if not course:
            return {'completed': 0, 'total': 0, 'completion_rate': 0}

        # 在 'obj' 中获取学生ID
        student_id = obj.get('student_id')
        try:
            # 需要导入User模型
            from users.models import User
            user = User.objects.get(id=student_id)
        except User.DoesNotExist:
            return {'completed': 0, 'total': 0, 'completion_rate': 0}

        # 任务点被定义为没有子节点的章节（即“节”）
        task_points = Chapter.objects.filter(course=course, parent__isnull=False)
        total_tasks = task_points.count()

        if total_tasks == 0:
            return {'completed': 0, 'total': 0, 'completion_rate': 0}

        completed_tasks = ChapterReadStatus.objects.filter(
            user=user,
            chapter__in=task_points
        ).count()
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        return {
            'completed': completed_tasks, 
            'total': total_tasks,
            'completion_rate': completion_rate
        }
