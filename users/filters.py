import django_filters
from .models import User

class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr='icontains')
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    school = django_filters.CharFilter(lookup_expr='icontains')
    student_id = django_filters.CharFilter(lookup_expr='icontains')
    role = django_filters.ChoiceFilter(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'school', 'student_id', 'role']
