from django.db import models
from users.models import User
from courses.models import Course

class Assignment(models.Model):
    """
    作业/考试模型
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments', verbose_name='所属课程')
    title = models.CharField(max_length=100, verbose_name='标题')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    due_date = models.DateTimeField(verbose_name='截止日期')

    def __str__(self):
        return self.title

class Question(models.Model):
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
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions', verbose_name='所属作业/考试')
    text = models.TextField(verbose_name='问题文本')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, verbose_name='问题类型')
    points = models.PositiveIntegerField(default=0, verbose_name='分值')
    correct_answer = models.TextField(blank=True, null=True, verbose_name='正确答案')

    def __str__(self):
        return self.text

class Choice(models.Model):
    """
    选择题选项模型
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name='所属问题')
    text = models.CharField(max_length=255, verbose_name='选项文本')
    is_correct = models.BooleanField(default=False, verbose_name='是否为正确答案')

    def __str__(self):
        return self.text

class Submission(models.Model):
    """
    学生提交记录模型
    """
    STATUS_CHOICES = (
        ('submitted', '已提交'),
        ('graded', '已批改'),
    )
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions', verbose_name='所提交的作业/考试')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions', verbose_name='提交学生')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')
    grade = models.FloatField(blank=True, null=True, verbose_name='分数')
    feedback = models.TextField(blank=True, null=True, verbose_name='教师评语')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='submitted', verbose_name='状态')

    def __str__(self):
        return f'{self.student.username} - {self.assignment.title}'

class Answer(models.Model):
    """
    学生答案模型
    """
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers', verbose_name='所属提交记录')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='所回答的问题')
    text = models.TextField(verbose_name='答案文本')
    score = models.FloatField(blank=True, null=True, verbose_name='得分')

    def __str__(self):
        return f'Answer to "{self.question.text}"'
