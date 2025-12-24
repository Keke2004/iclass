from rest_framework.permissions import BasePermission, SAFE_METHODS
from courses.models import Course
from .models import Exam


class CanRetrieveExam(BasePermission):
    """
    Allows teachers to always retrieve.
    Allows enrolled students to retrieve exam info.
    """
    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Exam):
            return False
        
        # Allow teacher of the course
        if obj.course.teacher == request.user:
            return True
        
        # Allow enrolled students for safe methods
        if request.method in SAFE_METHODS and request.user in obj.course.students.all():
            return True
        
        return False


class IsTeacherOfCourse(BasePermission):
    """
    Allows access only to the teacher of the course.
    """
    def has_object_permission(self, request, view, obj):
        # For Exam objects
        if hasattr(obj, 'course'):
            return obj.course.teacher == request.user
        return False

class IsEnrolledStudent(BasePermission):
    """
    Allows access only to students enrolled in the course.
    """
    def has_permission(self, request, view):
        # For actions that are not safe (e.g., POST, PUT), check for enrollment.
        if request.method not in SAFE_METHODS:
            # Try to get exam_id from the request data (for create action)
            exam_id = request.data.get('exam')
            # If not in data, try to get it from URL kwargs (for detail actions like start_exam)
            if not exam_id:
                exam_id = view.kwargs.get('pk') or view.kwargs.get('exam_id')

            if not exam_id:
                return False
            
            try:
                # Efficiently find the course associated with the exam
                exam = Exam.objects.select_related('course').get(id=exam_id)
                return request.user in exam.course.students.all()
            except Exam.DoesNotExist:
                return False
        
        # For SAFE_METHODS (GET, HEAD, OPTIONS), permission is granted.
        return True

class IsSubmissionOwnerOrTeacher(BasePermission):
    """
    Allows access only to the submission owner or the teacher of the course.
    """
    def has_object_permission(self, request, view, obj):
        # For ExamSubmission objects
        if hasattr(obj, 'student') and hasattr(obj, 'exam'):
            return obj.student == request.user or obj.exam.course.teacher == request.user
        return False
