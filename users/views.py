from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, MyTokenObtainPairSerializer, PasswordChangeSerializer
from .models import User
from .permissions import IsAdminRole

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    - Admins can view, edit, and delete any user.
    - Other authenticated users can only view the user list (e.g., for selecting students).
    """
    serializer_class = UserSerializer
    
    def get_queryset(self):
        """
        - Admins see all users.
        - Teachers/Students can see a list of users filtered by role.
        """
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return User.objects.all()
        
        queryset = User.objects.all()
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset

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
