from rest_framework import viewsets
from .models import Course, CourseMaterial, Announcement
from .serializers import CourseSerializer, CourseMaterialSerializer, AnnouncementSerializer

class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows courses to be viewed or edited.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

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
