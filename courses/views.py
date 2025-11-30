from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User
from .models import Course, CourseMaterial, Announcement
from .serializers import CourseSerializer, CourseMaterialSerializer, AnnouncementSerializer
from .permissions import IsTeacherOrReadOnly

class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows courses to be viewed or edited.
    - Teachers can create, update, and delete their own courses.
    - Students can only view courses.
    """
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]

    def get_queryset(self):
        """
        - Teachers see their own created courses.
        - Students see the courses they are enrolled in.
        - Admins see all courses.
        """
        user = self.request.user
        # The check `self.action == 'list'` is removed to apply the logic more broadly,
        # but the core filtering logic remains. Let's adjust it to be more robust.
        if self.action == 'list':
            if user.is_teacher:
                return Course.objects.filter(teacher=user)
            elif user.is_student:
                return user.enrolled_courses.all()
        # For create, retrieve, update, etc., we should allow access to all courses
        # and let permissions handle the object-level access.
        return Course.objects.all()

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
    queryset = CourseMaterial.objects.all()
    serializer_class = CourseMaterialSerializer

class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows announcements to be viewed or edited.
    """
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
