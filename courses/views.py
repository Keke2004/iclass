import os
import re
import mimetypes
import random
from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponse, Http404
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_exempt
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializers import UserSerializer
from .models import Course, CourseMaterial, Announcement, Chapter
from .serializers import (
    CourseSerializer, CourseListSerializer, CourseMaterialSerializer, 
    AnnouncementSerializer, ChapterSerializer, ChapterWriteSerializer,
    LearningRecordSerializer
)
from .permissions import IsTeacherOrReadOnly, IsCourseMember
from checkin.models import Checkin, CheckinRecord
from assignments.models import Assignment, Submission
from exams.models import Exam, ExamSubmission
from interaction.models import DiscussionTopic, DiscussionReply, RandomQuestion
from checkin.serializers import CheckinSerializer
from interaction.serializers import RandomQuestionSerializer
from itertools import chain

class ChapterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows chapters to be viewed or edited.
    """
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]

    def get_serializer_class(self):
        """
        根据操作（读取或写入）使用不同的序列化器。
        """
        if self.action in ['create', 'update', 'partial_update']:
            return ChapterWriteSerializer
        return ChapterSerializer

    def get_queryset(self):
        """
        Filter chapters by the course specified in the URL.
        - For list view, only top-level chapters are returned.
        - For detail view (retrieve, update, delete), all chapters are considered.
        """
        queryset = Chapter.objects.filter(course_id=self.kwargs['course_pk'])
        if self.action == 'list':
            return queryset.filter(parent__isnull=True)
        return queryset

    def perform_create(self, serializer):
        """
        Associate the chapter with the course from the URL.
        """
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        serializer.save(course=course)

class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows courses to be viewed or edited.
    - Teachers can create, update, and delete their own courses.
    - Students can only view courses.
    """
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]

    def get_serializer_class(self):
        """
        为列表视图使用轻量级序列化器，为详细视图使用完整序列化器。
        """
        if self.action == 'list':
            return CourseListSerializer
        return CourseSerializer

    def get_queryset(self):
        """
        - Teachers see their own created courses.
        - Students see the courses they are enrolled in.
        - Admins see all courses.
        """
        user = self.request.user
        if user.is_staff:  # Admins see all courses
            return Course.objects.all()
        if user.is_teacher:
            return Course.objects.filter(teacher=user)
        elif user.is_student:
            return user.enrolled_courses.all()
        return Course.objects.none()  # Default to no courses if role is not set

    def perform_create(self, serializer):
        """
        Set the teacher to the current user and assign a random cover image when creating a new course.
        """
        cover_images = [
            "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80",
            "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80",
            "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=928&q=80",
            "https://images.unsplash.com/photo-1523240795612-9a054b0db644?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80",
            "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80",
            "https://images.unsplash.com/photo-1588702547919-26089e690ecc?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1171&q=80",
        ]
        serializer.save(
            teacher=self.request.user,
            cover=random.choice(cover_images)
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsTeacherOrReadOnly])
    def add_student(self, request, pk=None):
        """
        Add a student to the course.
        """
        course = self.get_object()
        student_id = request.data.get('student_id')
        if not student_id:
            return Response({'error': 'Student ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            student = User.objects.get(id=student_id, role='student')
        except User.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

        course.students.add(student)
        return Response({'status': 'Student added successfully.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsTeacherOrReadOnly])
    def remove_student(self, request, pk=None):
        """
        Remove a student from the course.
        """
        course = self.get_object()
        student_id = request.data.get('student_id')
        if not student_id:
            return Response({'error': 'Student ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = User.objects.get(id=student_id, role='student')
        except User.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

        course.students.remove(student)
        return Response({'status': 'Student removed successfully.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def members(self, request, pk=None):
        """
        Get all members (students and teachers) of a course.
        """
        course = self.get_object()
        # 验证用户是否有权查看成员列表
        if not (request.user.is_staff or course.teacher == request.user or request.user in course.students.all()):
            return Response({"detail": "You do not have permission to view course members."}, status=status.HTTP_403_FORBIDDEN)
        
        # 同时获取教师和学生
        teacher = course.teacher
        students = course.students.all()
        
        # 使用 UserSerializer 序列化
        teacher_serializer = UserSerializer(teacher)
        students_serializer = UserSerializer(students, many=True)
        
        return Response({
            'teacher': teacher_serializer.data,
            'students': students_serializer.data
        })

class CourseMaterialViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows course materials to be viewed or edited.
    """
    serializer_class = CourseMaterialSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]

    def get_queryset(self):
        """
        - 仅返回当前用户有权访问的课程的资料。
        - 教师或学生可以查看他们所在课程的资料。
        """
        course_pk = self.kwargs['course_pk']
        user = self.request.user
        # 检查用户是否是该课程的教师或学生
        is_teacher = Course.objects.filter(pk=course_pk, teacher=user).exists()
        is_student = user.enrolled_courses.filter(pk=course_pk).exists()

        if is_teacher or is_student or user.is_staff:
            queryset = CourseMaterial.objects.filter(course_id=course_pk)
            search_query = self.request.query_params.get('search', None)
            if search_query:
                queryset = queryset.filter(name__icontains=search_query)
            return queryset
        
        # 如果用户无权访问，则返回空查询集
        return CourseMaterial.objects.none()

    def perform_create(self, serializer):
        """
        - 将资料与URL中的课程关联。
        - 自动设置上传者为当前用户。
        - 从上传的文件中提取文件名和大小。
        """
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        uploaded_file = self.request.data.get('file')
        
        if not uploaded_file:
            raise serializers.ValidationError("No file was submitted.")

        serializer.save(
            course=course,
            uploaded_by=self.request.user,
            name=uploaded_file.name,
            size=uploaded_file.size
        )

    @action(detail=True, methods=['get'])
    @xframe_options_exempt
    def download(self, request, pk=None, course_pk=None):
        """
        提供文件下载。
        在开发环境中直接提供文件，在生产环境中使用 X-Accel-Redirect。
        """
        material = self.get_object()
        file_handle = material.file

        if settings.DEBUG:
            # 在开发环境中，直接使用 FileResponse 发送文件
            try:
                # 使用 material.file.path 获取绝对路径，并设置为 inline 以便预览
                return FileResponse(open(material.file.path, 'rb'), as_attachment=False)
            except FileNotFoundError:
                return Response({"detail": "文件未找到。"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # 在生产环境中，继续使用 X-Accel-Redirect 以获得高性能
            response = Response(status=status.HTTP_200_OK)
            # Content-Type 将由 Nginx 设置
            response['Content-Disposition'] = f'attachment; filename="{material.name}"'
            response['X-Accel-Redirect'] = file_handle.url
            return response

    @action(detail=False, methods=['delete'], url_path='bulk_delete')
    def bulk_delete(self, request, course_pk=None):
        """
        批量删除课程资料。
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"detail": "未提供ID。"}, status=status.HTTP_400_BAD_REQUEST)

        # 验证用户是否有权限删除这些资料
        queryset = self.get_queryset().filter(id__in=ids)
        
        # 检查是否所有请求的ID都在用户有权访问的查询集中
        if queryset.count() != len(ids):
            return Response({"detail": "您没有权限删除某些指定的资料。"}, status=status.HTTP_403_FORBIDDEN)

        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows announcements to be viewed or edited.
    """
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]

    def get_queryset(self):
        """
        Filter announcements by the course specified in the URL.
        """
        return Announcement.objects.filter(course_id=self.kwargs['course_pk'])

    def perform_create(self, serializer):
        """
        Associate the announcement with the course from the URL.
        """
        course = Course.objects.get(pk=self.kwargs['course_pk'])
        serializer.save(course=course)


def ranged_media_view(request, path):
    """
    A view that serves media files and supports HTTP Range requests.
    This is necessary for video seeking (fast-forwarding and rewinding) in browsers.
    """
    # Construct the full path to the file
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    
    # Check if the file exists
    if not os.path.exists(full_path):
        raise Http404("File not found")

    # Get file size and content type
    file_size = os.path.getsize(full_path)
    content_type, _ = mimetypes.guess_type(full_path)
    content_type = content_type or 'application/octet-stream'
    
    # Handle Range header
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
    range_match = range_re.match(range_header)
    
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = int(last_byte) if last_byte else file_size - 1
        
        if last_byte >= file_size:
            last_byte = file_size - 1
            
        length = last_byte - first_byte + 1
        
        response = HttpResponse(status=206)
        response['Content-Type'] = content_type
        response['Content-Length'] = str(length)
        response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{file_size}'
        response['Accept-Ranges'] = 'bytes'
        
        with open(full_path, 'rb') as f:
            f.seek(first_byte)
            response.content = f.read(length)
        
        return response
    else:
        # Serve the whole file if no Range header
        response = FileResponse(open(full_path, 'rb'), content_type=content_type)
        response['Content-Length'] = str(file_size)
        response['Accept-Ranges'] = 'bytes'
        return response

class LearningRecordView(APIView):
    """
    获取单个学生或整个课程的学习记录
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        user = request.user

        # 验证用户权限
        if not (user.is_staff or course.teacher == user or user in course.students.all()):
            return Response({"detail": "您没有权限查看此课程的学习记录。"}, status=status.HTTP_403_FORBIDDEN)

        # 教师或管理员可以查看指定学生或所有学生
        if user.is_teacher or user.is_staff:
            student_id = request.query_params.get('student_id')
            if student_id:
                try:
                    students_to_process = [User.objects.get(id=student_id, enrolled_courses=course)]
                except User.DoesNotExist:
                    return Response({"detail": "学生不存在或未加入该课程。"}, status=status.HTTP_404_NOT_FOUND)
            else:
                students_to_process = course.students.all()
        else: # 学生只能查看自己的记录
            students_to_process = [user]

        learning_records = []
        for student in students_to_process:
            # 1. 签到统计
            total_checkins = Checkin.objects.filter(course=course).count()
            student_records = CheckinRecord.objects.filter(checkin__course=course, student=student)
            
            checkin_summary = {
                'total': total_checkins,
                'present': student_records.filter(status='present').count(),
                'late': student_records.filter(status='late').count(),
                'absent': total_checkins - student_records.exclude(status='absent').count(), # 缺勤 = 总数 - 非缺勤
                'sick_leave': student_records.filter(status='sick_leave').count(),
                'personal_leave': student_records.filter(status='personal_leave').count(),
            }
            # 出勤率 = (出勤 + 迟到) / 总数
            attendance_count = checkin_summary['present'] + checkin_summary['late']
            checkin_summary['attendance_rate'] = (attendance_count / total_checkins * 100) if total_checkins > 0 else 0

            # 2. 作业统计
            total_assignments = Assignment.objects.filter(course=course).count()
            completed_assignments = Submission.objects.filter(assignment__course=course, student=student).count()
            assignment_summary = {
                'total': total_assignments,
                'completed': completed_assignments,
                'completion_rate': (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0
            }

            # 3. 考试统计
            total_exams = Exam.objects.filter(course=course).count()
            completed_exams = ExamSubmission.objects.filter(exam__course=course, student=student, status__in=['submitted', 'graded']).count()
            exam_summary = {
                'total': total_exams,
                'completed': completed_exams,
                'completion_rate': (completed_exams / total_exams * 100) if total_exams > 0 else 0
            }

            # 4. 讨论统计
            discussion_summary = {
                'topic_count': DiscussionTopic.objects.filter(course=course, author=student).count(),
                'reply_count': DiscussionReply.objects.filter(topic__course=course, author=student).count(),
            }

            learning_records.append({
                'student_id': student.id,
                'student_name': student.get_full_name() or student.username,
                'checkin_summary': checkin_summary,
                'assignment_summary': assignment_summary,
                'exam_summary': exam_summary,
                'discussion_summary': discussion_summary,
            })
        
        # 注意：由于数据结构已更改，旧的 LearningRecordSerializer 可能不再适用
        # 我们直接返回字典列表，DRF 会自动处理 JSON 序列化
        return Response(learning_records)


class TaskListView(APIView):
    """
    获取课程的统一任务列表，包括签到和随机提问。
    """
    permission_classes = [permissions.IsAuthenticated, IsCourseMember]

    def get(self, request, course_id):
        # 验证课程是否存在
        course = get_object_or_404(Course, pk=course_id)

        # 获取所有签到任务
        checkins = Checkin.objects.filter(course=course)
        checkin_data = CheckinSerializer(checkins, many=True, context={'request': request}).data
        for item in checkin_data:
            item['task_type'] = 'checkin'

        # 获取所有随机提问任务
        random_questions = RandomQuestion.objects.filter(course=course)
        random_question_data = RandomQuestionSerializer(random_questions, many=True, context={'request': request}).data
        for item in random_question_data:
            item['task_type'] = 'random_question'
            item['title'] = f"随机提问 - {item['student']['username']}"
            item['start_time'] = item['created_at']
            item['is_active'] = False  # 随机提问是即时完成的

        # 合并并按开始时间降序排序
        combined_tasks = sorted(
            chain(checkin_data, random_question_data),
            key=lambda x: x.get('start_time'),
            reverse=True
        )

        return Response(combined_tasks)
