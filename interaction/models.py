from django.db import models
from users.models import User
from courses.models import Course

class Attendance(models.Model):
    """
    签到记录模型
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendances', verbose_name='所属课程')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances', verbose_name='签到学生')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='签到时间')

    def __str__(self):
        return f'{self.student.username} - {self.course.name}'

class Question(models.Model):
    """
    课堂提问模型
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='live_questions', verbose_name='所属课程')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asked_questions', verbose_name='提问学生')
    text = models.TextField(verbose_name='问题内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='提问时间')

    def __str__(self):
        return self.text

class Vote(models.Model):
    """
    投票模型
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='votes', verbose_name='所属课程')
    title = models.CharField(max_length=255, verbose_name='投票标题')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.title

class VoteChoice(models.Model):
    """
    投票选项模型
    """
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, related_name='choices', verbose_name='所属投票')
    text = models.CharField(max_length=255, verbose_name='选项内容')

    def __str__(self):
        return self.text

class VoteResponse(models.Model):
    """
    学生投票响应模型
    """
    choice = models.ForeignKey(VoteChoice, on_delete=models.CASCADE, related_name='responses', verbose_name='所选选项')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vote_responses', verbose_name='投票学生')
    voted_at = models.DateTimeField(auto_now_add=True, verbose_name='投票时间')

    class Meta:
        unique_together = ('choice', 'student')

class Discussion(models.Model):
    """
    课堂讨论模型
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='discussions', verbose_name='所属课程')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussion_messages', verbose_name='发言学生')
    message = models.TextField(verbose_name='消息内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发言时间')

    def __str__(self):
        return f'{self.student.username}: {self.message[:50]}'
