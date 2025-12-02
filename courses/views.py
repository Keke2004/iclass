from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
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
        Filter materials by the course specified in the URL.
        """
        return CourseMaterial.objects.filter(course_id=self.kwargs['course_pk'])

    def perform_create(self, serializer):
        """
        Associate the material with the course from the URL.
        """
        course = Course.objects.get(pk=self.kwargs['course_pk'])
        serializer.save(course=course)

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
