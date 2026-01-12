from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from assignments.models import Assignment, Submission
from exams.models import Exam, ExamSubmission
from checkin.models import Checkin, CheckinRecord
from interaction.models import DiscussionTopic, Question, Vote, VoteResponse, RandomQuestion
from feedback.models import Questionnaire, FeedbackResponse
from courses.models import Announcement
from .models import Notification

@receiver(post_save, sender=Announcement)
def create_announcement_notification(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        for student in course.students.all():
            Notification.objects.create(
                recipient=student,
                sender=course.teacher,
                message=f"课程\"{course.name}\"中发布了新公告：'{instance.title}'。",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )

@receiver(post_save, sender=Questionnaire)
def create_questionnaire_notification(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        for student in course.students.all():
            Notification.objects.create(
                recipient=student,
                sender=course.teacher,
                message=f"课程\"{course.name}\"中发布了新反馈：'{instance.title}'。",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )

@receiver(post_save, sender=FeedbackResponse)
def create_feedback_response_notification(sender, instance, created, **kwargs):
    if created:
        questionnaire = instance.questionnaire
        course = questionnaire.course
        student_name = instance.student.username if instance.student else "Anonymous"
        Notification.objects.create(
            recipient=course.teacher,
            sender=instance.student,
            message=f"学生 {student_name} 提交了反馈\"{questionnaire.title}\"。",
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )

@receiver(post_save, sender=Vote)
def create_vote_notification(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        for student in course.students.all():
            Notification.objects.create(
                recipient=student,
                sender=course.teacher,
                message=f"课程\"{course.name}\"中发起了新投票：'{instance.title}'。",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )

@receiver(post_save, sender=VoteResponse)
def create_vote_response_notification(sender, instance, created, **kwargs):
    if created:
        vote = instance.vote
        course = vote.course
        Notification.objects.create(
            recipient=course.teacher,
            sender=instance.student,
            message=f"学生 {instance.student.username} 在投票“{vote.title}”中进行了投票。",
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )

@receiver(post_save, sender=Question)
def create_question_notification(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        teacher = instance.student  # The creator is the teacher
        for student in course.students.all():
            Notification.objects.create(
                recipient=student,
                sender=teacher,
                message=f"老师在课程\"{course.name}\"中发布了一个新提问。",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )

@receiver(post_save, sender=RandomQuestion)
def create_random_question_notification(sender, instance, created, **kwargs):
    # Trigger when a student is assigned (update), not on initial creation.
    if not created and instance.student:
        course = instance.course
        content_type = ContentType.objects.get_for_model(instance)
        
        # Prevent duplicate notifications on subsequent saves.
        if not Notification.objects.filter(
            recipient=instance.student,
            content_type=content_type,
            object_id=instance.id
        ).exists():
            Notification.objects.create(
                recipient=instance.student,
                sender=course.teacher,
                message=f"您在课程\"{course.name}\"中被选中进行随机提问。",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )

@receiver(post_save, sender=DiscussionTopic)
def create_discussion_topic_notification(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        # Notify all students except the author
        for student in course.students.all():
            if student != instance.author:
                Notification.objects.create(
                    recipient=student,
                    sender=instance.author,
                    message=f"课程\"{course.name}\"中发布了新讨论：'{instance.title}'。",
                    content_type=ContentType.objects.get_for_model(instance),
                    object_id=instance.id
                )
        # Notify the teacher if the author is not the teacher
        if course.teacher != instance.author:
            Notification.objects.create(
                recipient=course.teacher,
                sender=instance.author,
                message=f"课程\"{course.name}\"中发布了新讨论：'{instance.title}'。",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )

@receiver(post_save, sender=Checkin)
def create_checkin_notification(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        for student in course.students.all():
            Notification.objects.create(
                recipient=student,
                sender=course.teacher,
                message=f"课程\"{course.name}\"开始了新的签到。",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )

@receiver(post_save, sender=CheckinRecord)
def create_checkin_record_notification(sender, instance, created, **kwargs):
    if created:
        checkin = instance.checkin
        course = checkin.course
        Notification.objects.create(
            recipient=course.teacher,
            sender=instance.student,
            message=f"学生 {instance.student.username} 已在“{checkin.title}”中签到。",
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )

@receiver(post_save, sender=Exam)
def create_exam_notification(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        for student in course.students.all():
            Notification.objects.create(
                recipient=student,
                sender=course.teacher,
                message=f"课程\"{course.name}\"中发布了新考试：'{instance.title}'。",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )

@receiver(post_save, sender=ExamSubmission)
def create_exam_submission_notification(sender, instance, created, **kwargs):
    if created:
        exam = instance.exam
        course = exam.course
        Notification.objects.create(
            recipient=course.teacher,
            sender=instance.student,
            message=f"学生 {instance.student.username} 提交了考试\"{exam.title}\"。",
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )

@receiver(post_save, sender=Submission)
def create_submission_notification(sender, instance, created, **kwargs):
    if created:
        assignment = instance.assignment
        course = assignment.course
        Notification.objects.create(
            recipient=course.teacher,
            sender=instance.student,
            message=f"学生 {instance.student.username} 提交了作业\"{assignment.title}\"。",
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )

@receiver(post_save, sender=Assignment)
def create_assignment_notification(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        for student in course.students.all():
            Notification.objects.create(
                recipient=student,
                sender=course.teacher,
                message=f"课程\"{course.name}\"中发布了新作业：'{instance.title}'。",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )
