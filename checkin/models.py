from django.db import models
from courses.models import Course
from users.models import User

class Checkin(models.Model):
    """
    签到任务模型
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='checkins')
    title = models.CharField(max_length=255, default='签到')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course.name} - {self.title}"

class CheckinRecord(models.Model):
    """
    学生签到记录模型
    """
    STATUS_CHOICES = (
        ('present', '出勤'),
        ('late', '迟到'),
        ('absent', '缺勤'),
        ('sick_leave', '病假'),
        ('personal_leave', '事假'),
    )

    checkin = models.ForeignKey(Checkin, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkin_records')
    checkin_time = models.DateTimeField(null=True, blank=True, verbose_name="签到时间")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present',
        verbose_name="签到状态"
    )
    is_manual = models.BooleanField(default=False, verbose_name="是否为手动操作") # 标记是否为教师代签或学生请假

    class Meta:
        unique_together = ('checkin', 'student')
        verbose_name = "签到记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.student.username} - {self.checkin.title}: {self.get_status_display()}"
