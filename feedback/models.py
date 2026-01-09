from django.db import models
from users.models import User
from courses.models import Course

class Questionnaire(models.Model):
    """
    教学问卷模型
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='questionnaires', verbose_name='所属课程')
    title = models.CharField(max_length=255, verbose_name='问卷标题')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.title

class FeedbackQuestion(models.Model):
    """
    问卷问题模型
    """
    QUESTION_TYPE_CHOICES = (
        ('rating', '评分题'),
        ('text', '文本题'),
    )
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='questions', verbose_name='所属问卷')
    text = models.TextField(verbose_name='问题内容')
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES, default='text', verbose_name='问题类型')

    def __str__(self):
        return self.text

class FeedbackResponse(models.Model):
    """
    学生反馈提交记录模型
    """
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='responses', verbose_name='所属问卷')
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedback_responses', verbose_name='提交学生 (可匿名)')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')

    def __str__(self):
        student_name = self.student.username if self.student else "Anonymous"
        return f'Response to "{self.questionnaire.title}" by {student_name}'

class FeedbackAnswer(models.Model):
    """
    学生反馈答案模型
    """
    response = models.ForeignKey(FeedbackResponse, on_delete=models.CASCADE, related_name='answers', verbose_name='所属反馈')
    question = models.ForeignKey(FeedbackQuestion, on_delete=models.CASCADE, related_name='answers', verbose_name='所属问题')
    answer_text = models.TextField(blank=True, null=True, verbose_name='文本答案')
    answer_rating = models.IntegerField(blank=True, null=True, verbose_name='评分答案')

    def __str__(self):
        return f'Answer to "{self.question.text}"'
