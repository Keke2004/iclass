from django.db import models
from users.models import User

class Course(models.Model):
    """
    课程模型
    """
    name = models.CharField(max_length=100, verbose_name='课程名称')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_courses', verbose_name='授课教师')
    students = models.ManyToManyField(User, related_name='enrolled_courses', blank=True, verbose_name='课程学生')
    description = models.TextField(blank=True, null=True, verbose_name='课程描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.name

class CourseMaterial(models.Model):
    """
    课程资料模型
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials', verbose_name='所属课程')
    title = models.CharField(max_length=100, verbose_name='资料标题')
    file = models.FileField(upload_to='course_materials/', verbose_name='文件')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    def __str__(self):
        return self.title

class Announcement(models.Model):
    """
    课程公告模型
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='announcements', verbose_name='所属课程')
    title = models.CharField(max_length=100, verbose_name='公告标题')
    content = models.TextField(verbose_name='公告内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')

    def __str__(self):
        return self.title
