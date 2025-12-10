from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.conf import settings
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User
from .models import Course, CourseMaterial, Announcement, Chapter
from .serializers import CourseSerializer, CourseListSerializer, CourseMaterialSerializer, AnnouncementSerializer, ChapterSerializer
from .permissions import IsTeacherOrReadOnly

class ChapterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows chapters to be viewed or edited.
    """
    serializer_class = ChapterSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]

    def get_queryset(self):
        """
        Filter chapters by the course specified in the URL.
        """
        return Chapter.objects.filter(course_id=self.kwargs['course_pk'])

    def get_object(self):
        """
        Retrieve a specific chapter by its pk, filtered by the course_pk.
        """
        queryset = self.get_queryset()
        chapter = get_object_or_404(queryset, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, chapter)
        return chapter

    def perform_create(self, serializer):
        """
        Associate the chapter with the course from the URL.
        """
        course = Course.objects.get(pk=self.kwargs['course_pk'])
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
        Set the teacher to the current user when creating a new course.
        """
        serializer.save(teacher=self.request.user)

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
