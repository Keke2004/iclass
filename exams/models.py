from django.db import models
from users.models import User
from courses.models import Course

class Exam(models.Model):
    """
    考试模型
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams', verbose_name='所属课程')
    title = models.CharField(max_length=100, verbose_name='标题')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    start_time = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_time = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)
    time_limit = models.PositiveIntegerField(default=60, verbose_name='考试时长(分钟)')

    def __str__(self):
        return self.title

class ExamQuestion(models.Model):
    """
    问题模型
    """
    QUESTION_TYPE_CHOICES = (
        ('single_choice', '单选题'),
        ('multiple_choice', '多选题'),
        ('true_false', '判断题'),
        ('fill_in_the_blank', '填空题'),
        ('short_answer', '简答题'),
    )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions', verbose_name='所属考试')
    text = models.TextField(verbose_name='问题文本')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, verbose_name='问题类型')
    points = models.PositiveIntegerField(default=0, verbose_name='分值')
    correct_answer = models.TextField(blank=True, null=True, verbose_name='正确答案')

    def __str__(self):
        return self.text

class ExamChoice(models.Model):
    """
    选择题选项模型
    """
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE, related_name='choices', verbose_name='所属问题')
    text = models.CharField(max_length=255, verbose_name='选项文本')
    is_correct = models.BooleanField(default=False, verbose_name='是否为正确答案')

    def __str__(self):
        return self.text

class ExamSubmission(models.Model):
    """
    学生提交记录模型
    """
    STATUS_CHOICES = (
        ('taking', '正在进行'),
        ('submitted', '已提交'),
        ('graded', '已批改'),
    )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='submissions', verbose_name='所提交的考试')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_submissions', verbose_name='提交学生')
    start_time = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')
    grade = models.FloatField(blank=True, null=True, verbose_name='分数')
    feedback = models.TextField(blank=True, null=True, verbose_name='教师评语')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='taking', verbose_name='状态')

    def __str__(self):
        return f'{self.student.username} - {self.exam.title}'

    class Meta:
        unique_together = ('exam', 'student')


class ExamAnswer(models.Model):
    """
    学生答案模型
    """
    submission = models.ForeignKey(ExamSubmission, on_delete=models.CASCADE, related_name='answers', verbose_name='所属提交记录')
    question = models.ForeignKey(ExamQuestion, on_delete=models.SET_NULL, null=True, related_name='answers', verbose_name='所回答的问题')
    text = models.TextField(verbose_name='答案文本')
    score = models.FloatField(blank=True, null=True, verbose_name='得分')

    def __str__(self):
        return f'Answer to "{self.question.text}"'
