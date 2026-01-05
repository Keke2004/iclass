from rest_framework import permissions
from .models import Course

class IsCourseMember(permissions.BasePermission):
    """
    Custom permission to only allow members of a course to view it.
    """
    def has_permission(self, request, view):
        course_id = view.kwargs.get('course_pk') or view.kwargs.get('course_id') or view.kwargs.get('pk')
        if not course_id:
            return False
        
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return False
            
        return request.user in course.students.all() or request.user == course.teacher

class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow teachers to edit objects.
    Students and other users can only view them.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the users who are teachers.
        return request.user and request.user.is_authenticated and request.user.is_teacher

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the teacher who owns the course.
        if hasattr(obj, 'course'):
            return obj.course.teacher == request.user
        return obj.teacher == request.user

class IsAuthorOrTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object or the course teacher to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the object or the course teacher.
        return obj.author == request.user or obj.course.teacher == request.user

class IsCourseTeacher(permissions.BasePermission):
    """
    Permission to only allow the teacher of the course to perform an action.
    """
    def has_permission(self, request, view):
        course_id = view.kwargs.get('course_pk') or view.kwargs.get('course_id')
        if not course_id:
            return False
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return False
        return course.teacher == request.user

class IsCourseStudent(permissions.BasePermission):
    """
    Permission to only allow students of the course to perform an action.
    """
    def has_permission(self, request, view):
        course_id = view.kwargs.get('course_pk') or view.kwargs.get('course_id')
        if not course_id:
            return False
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return False
        return request.user in course.students.all()
