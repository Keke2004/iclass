from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Checkin, CheckinRecord
from .serializers import CheckinSerializer, CheckinRecordSerializer
from courses.models import Course
from users.models import User
from courses.permissions import IsCourseTeacher, IsCourseStudent

class CheckinViewSet(viewsets.ModelViewSet):
    queryset = Checkin.objects.all()
    serializer_class = CheckinSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_pk = self.kwargs.get('course_pk')
        return self.queryset.filter(course_id=course_pk).order_by('-start_time')

    def get_permissions(self):
        if self.action in ['create', 'end_checkin', 'proxy_checkin', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsCourseTeacher]
        elif self.action in ['student_checkin']:
            self.permission_classes = [IsAuthenticated, IsCourseStudent]
        return super().get_permissions()

    def perform_create(self, serializer):
        course = Course.objects.get(pk=self.kwargs.get('course_pk'))
        serializer.save(course=course)

    @action(detail=True, methods=['post'])
    def end_checkin(self, request, pk=None, course_pk=None):
        checkin = self.get_object()
        checkin.is_active = False
        checkin.save()
        return Response({'status': 'Check-in ended'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def student_checkin(self, request, pk=None, course_pk=None):
        checkin = self.get_object()
        if not checkin.is_active:
            return Response({'error': 'Check-in is not active'}, status=status.HTTP_400_BAD_REQUEST)
        
        record, created = CheckinRecord.objects.get_or_create(
            checkin=checkin,
            student=request.user
        )

        if not created:
            return Response({'error': 'You have already checked in'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CheckinRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def proxy_checkin(self, request, pk=None, course_pk=None):
        student_id = request.data.get('student_id')
        if not student_id:
            return Response({'error': 'Student ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        checkin = self.get_object()
        try:
            student = User.objects.get(pk=student_id)
        except User.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        record, created = CheckinRecord.objects.get_or_create(
            checkin=checkin,
            student=student,
            defaults={'is_manual': True}
        )

        if not created:
            return Response({'error': 'Student has already checked in'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CheckinRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
