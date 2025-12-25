import json
import datetime
from django.utils import timezone
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Exam, ExamQuestion, ExamSubmission, ExamAnswer
from .serializers import ExamSerializer, ExamSubmissionSerializer
from .permissions import IsTeacherOfCourse, IsSubmissionOwnerOrTeacher, IsEnrolledStudent, CanRetrieveExam
from rest_framework.generics import ListAPIView


class SubmissionsForExamView(ListAPIView):
    serializer_class = ExamSubmissionSerializer
    permission_classes = [IsAuthenticated, IsTeacherOfCourse]

    def get_queryset(self):
        exam_id = self.kwargs['exam_id']
        # The permission class will check if the user is the teacher of the course
        # associated with this exam.
        return ExamSubmission.objects.filter(exam_id=exam_id)


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated, IsTeacherOfCourse]

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated, CanRetrieveExam]
        elif self.action == 'start_exam':
            self.permission_classes = [IsAuthenticated, IsEnrolledStudent]
        else:
            self.permission_classes = [IsAuthenticated, IsTeacherOfCourse]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        queryset = Exam.objects.all()

        if not (user.is_staff or user.is_superuser):
            teacher_courses = user.teaching_courses.all()
            student_courses = user.enrolled_courses.all()
            queryset = queryset.filter(
                Q(course__in=teacher_courses) | Q(course__in=student_courses)
            ).distinct()

        status = self.request.query_params.get('status')
        if status:
            now = timezone.now()
            if user.role == 'teacher':
                if status == 'grading':
                    # Filter for exams that have submissions but not all are graded
                    queryset = [
                        exam for exam in queryset 
                        if exam.submissions.count() > 0 and 
                           exam.submissions.filter(status='graded').count() < exam.course.students.count()
                    ]
                elif status == 'graded_completed':
                    # Filter for exams where all students' submissions are graded
                    queryset = [
                        exam for exam in queryset 
                        if exam.submissions.filter(status='graded').count() == exam.course.students.count()
                    ]
            elif user.role == 'student':
                if status == 'pending':
                    # Not submitted and not past the end time
                    queryset = queryset.exclude(
                        submissions__student=user
                    ).filter(end_time__gte=now)
                elif status == 'completed':
                    # Submitted or graded
                    queryset = queryset.filter(
                        submissions__student=user, 
                        submissions__status__in=['submitted', 'graded']
                    )
        
        return queryset

    def perform_create(self, serializer):
        self.validate_exam_times(serializer.validated_data)
        serializer.save()

    def perform_update(self, serializer):
        self.validate_exam_times(serializer.validated_data)
        serializer.save()

    def update(self, request, *args, **kwargs):
        # The default update behavior is sufficient.
        # The problematic re-grading logic that was here has been removed
        # to prevent student scores from being reset when an exam is edited.
        # Auto-grading now only happens upon submission, consistent with the assignments module.
        return super().update(request, *args, **kwargs)

    def validate_exam_times(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        time_limit = data.get('time_limit')

        if start_time and end_time:
            if start_time >= end_time:
                raise serializers.ValidationError("结束时间必须晚于开始时间。")
            
            if time_limit and (end_time - start_time) < datetime.timedelta(minutes=time_limit):
                raise serializers.ValidationError("考试时间范围必须大于或等于考试时长。")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        show_answers = False

        if user.role == 'teacher' or user.is_staff or user.is_superuser:
            show_answers = True
        elif user.role == 'student':
            if ExamSubmission.objects.filter(exam=instance, student=user, status='graded').exists():
                show_answers = True
        
        context = self.get_serializer_context()
        context['show_answers'] = show_answers
        
        serializer = self.get_serializer(instance, context=context)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='start')
    def start_exam(self, request, pk=None):
        exam = self.get_object()
        student = request.user

        # Check if submission already exists
        submission, created = ExamSubmission.objects.get_or_create(
            exam=exam,
            student=student,
            defaults={'status': 'taking'}
        )

        if not created:
            if submission.status == 'taking':
                # If the exam is already in 'taking' status, it's not an error, just return the submission.
                pass
            else:
                # If the exam is in another status (e.g., 'submitted', 'graded'), it's a bad request.
                return Response(
                    {'detail': 'You have already completed this exam.', 'submission_id': submission.id},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = ExamSubmissionSerializer(submission)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExamSubmissionViewSet(viewsets.ModelViewSet):
    queryset = ExamSubmission.objects.all()
    serializer_class = ExamSubmissionSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsEnrolledStudent]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'grade', 'submit_exam']:
            self.permission_classes = [IsAuthenticated, IsSubmissionOwnerOrTeacher]
        else: # list action
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff or user.is_superuser:
            queryset = ExamSubmission.objects.all()
        elif user.role == 'student':
            queryset = ExamSubmission.objects.filter(student=user)
        elif user.role == 'teacher':
            teacher_courses = user.teaching_courses.all()
            queryset = ExamSubmission.objects.filter(exam__course__in=teacher_courses)
        else:
            queryset = ExamSubmission.objects.none()

        exam_id = self.request.query_params.get('exam')
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
            
        return queryset

    @action(detail=True, methods=['post'], url_path='submit')
    def submit_exam(self, request, pk=None):
        submission = self.get_object()
        
        # Check if the submission is by the right student and is in 'taking' state
        if submission.student != request.user or submission.status != 'taking':
            return Response({'detail': 'Invalid action.'}, status=status.HTTP_403_FORBIDDEN)

        # Time validation
        time_elapsed = timezone.now() - submission.start_time
        if time_elapsed > datetime.timedelta(minutes=submission.exam.time_limit):
            return Response({'detail': 'Exam time has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        answers_data = request.data.get('answers', [])
        submission.answers.all().delete() # Clear previous answers if any
        
        total_score = 0
        has_manual_grading = False

        for answer_data in answers_data:
            question_id = answer_data.get('question')
            answer_text = answer_data.get('text')
            question = ExamQuestion.objects.get(id=question_id)
            
            answer = ExamAnswer.objects.create(
                submission=submission,
                question=question,
                text=answer_text
            )

            is_correct = False
            if question.question_type == 'single_choice':
                correct_choice = question.choices.filter(is_correct=True).first()
                if correct_choice and answer.text == str(correct_choice.id):
                    is_correct = True
            
            elif question.question_type == 'multiple_choice':
                try:
                    student_answer_ids = sorted(json.loads(answer.text))
                    correct_choice_ids = sorted([str(pk) for pk in question.choices.filter(is_correct=True).values_list('id', flat=True)])
                    if student_answer_ids == correct_choice_ids:
                        is_correct = True
                except (json.JSONDecodeError, TypeError):
                    is_correct = False

            elif question.question_type in ['true_false', 'fill_in_the_blank']:
                if answer.text == question.correct_answer:
                    is_correct = True

            elif question.question_type == 'short_answer':
                has_manual_grading = True
                continue

            if is_correct:
                answer.score = question.points
            else:
                answer.score = 0
            
            answer.save()
            if answer.score:
                total_score += answer.score

        submission.grade = total_score
        submission.status = 'submitted' if has_manual_grading else 'graded'
        submission.submitted_at = timezone.now()
        submission.save()

        response_serializer = self.get_serializer(submission)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='grade')
    def grade(self, request, pk=None):
        submission = self.get_object()
        
        if request.user.role != 'teacher' or request.user != submission.exam.course.teacher:
            return Response({'detail': 'You do not have permission to grade this submission.'}, status=status.HTTP_403_FORBIDDEN)

        answers_data = request.data.get('answers', [])
        feedback = request.data.get('feedback')

        total_score = 0
        for answer_data in answers_data:
            try:
                answer = ExamAnswer.objects.get(id=answer_data['id'], submission=submission)
                score = answer_data.get('score', 0)
                if score > answer.question.points:
                    score = answer.question.points
                answer.score = score
                answer.save()
                total_score += score
            except (ExamAnswer.DoesNotExist, KeyError):
                continue

        submission.grade = total_score
        submission.feedback = feedback
        submission.status = 'graded'
        submission.save()

        serializer = self.get_serializer(submission)
        return Response(serializer.data, status=status.HTTP_200_OK)
