from rest_framework import permissions

class IsTeacherOfCourse(permissions.BasePermission):
    """
    自定义权限，只允许课程的教师进行写操作（创建、更新、删除）。
    """
    def has_permission(self, request, view):
        # 对列表视图（GET），所有认证用户都可以访问
        if request.method in permissions.SAFE_METHODS:
            return True
        # 对创建操作（POST），需要进一步的对象级权限检查
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 对安全方法（GET, HEAD, OPTIONS），允许所有相关人员访问
        if request.method in permissions.SAFE_METHODS:
            # 检查用户是否是教师或注册学生
            is_teacher = obj.course.teacher == request.user
            is_enrolled = request.user in obj.course.students.all()
            return is_teacher or is_enrolled
        
        # 对写操作，只允许课程的教师
        return obj.course.teacher == request.user

class IsSubmissionOwnerOrTeacher(permissions.BasePermission):
    """
    自定义权限，允许提交者（学生）或课程教师访问提交记录。
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # 提交记录的所有者（学生）可以访问
        if obj.student == request.user:
            return True
        
        # 作业所属课程的教师可以访问
        if obj.assignment.course.teacher == request.user:
            return True
            
        return False

class IsEnrolledStudent(permissions.BasePermission):
    """
    自定义权限，只允许注册了该课程的学生进行操作（例如，提交作业）。
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.data.get('assignment'):
            return False
        
        from .models import Assignment
        try:
            assignment = Assignment.objects.get(pk=request.data['assignment'])
            # 检查用户是否是该课程的注册学生
            return request.user in assignment.course.students.all()
        except Assignment.DoesNotExist:
            return False
