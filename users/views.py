from rest_framework import viewsets, permissions, generics, status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, MyTokenObtainPairSerializer, PasswordChangeSerializer
from .models import User
from .permissions import IsAdminRole
from .filters import UserFilter
from logs.models import Log

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            username = request.data.get('username')
            Log.objects.create(
                level='INFO',
                message=f'用户 {username} 登录成功'
            )
        return response

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    - Admins can view, edit, and delete any user.
    - Other authenticated users can only view the user list (e.g., for selecting students).
    """
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter
    
    def get_queryset(self):
        """
        - Admins see all users.
        - Teachers/Students can see a list of users filtered by role.
        - Can exclude users from a specific course.
        """
        user = self.request.user
        queryset = User.objects.all()

        # Exclude users from a specific course if `exclude_course` is provided
        exclude_course_id = self.request.query_params.get('exclude_course')
        if exclude_course_id:
            try:
                # We need to import Course model here to avoid circular dependency
                from courses.models import Course
                course = Course.objects.get(id=exclude_course_id)
                queryset = queryset.exclude(id__in=course.students.all())
            except (Course.DoesNotExist, ValueError):
                # Handle cases where course_id is invalid or not found
                pass

        if user.is_staff or user.role == 'admin':
            return queryset.order_by('id')
        
        # For non-admin users, default to showing only students and teachers
        return queryset.filter(role__in=['student', 'teacher']).order_by('id')

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        - `AllowAny` for registration (`create` action if `pk` is not present).
        - `IsAdminUser` for destructive actions (`update`, `destroy`).
        - `IsAuthenticated` for listing users.
        """
        if self.action == 'create':
            self.permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminRole]
        else: # list, retrieve
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "密码修改成功"}, status=status.HTTP_200_OK)

class UserStatisticsView(APIView):
    """
    API endpoint to get user statistics.
    - Only accessible by admins.
    - Provides counts of users by role.
    """
    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        role_counts = User.objects.values('role').annotate(count=Count('id'))
        
        # The result is a list of dicts, e.g., [{'role': 'student', 'count': 10}]
        # We can format this for a more consistent response structure if needed.
        data = {item['role']: item['count'] for item in role_counts}
        
        return Response(data, status=status.HTTP_200_OK)
