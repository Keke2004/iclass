from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', '学生'),
        ('teacher', '教师'),
        ('admin', '管理员'),
    )
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student', verbose_name='角色')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='性别')
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name='手机号')
    school = models.CharField(max_length=100, blank=True, null=True, verbose_name='单位/学校')
    student_id = models.CharField(max_length=20, blank=True, null=True, verbose_name='学号/工号')

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __str__(self):
        return self.username
