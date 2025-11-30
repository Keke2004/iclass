from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, MyTokenObtainPairSerializer
from .models import User

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
            self.permission_classes = [permissions.IsAdminUser]
        else: # list, retrieve
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
