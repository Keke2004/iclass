import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q

from .models import Assignment, Submission, Answer
from .serializers import AssignmentSerializer, SubmissionSerializer
from .permissions import IsTeacherOfCourse, IsSubmissionOwnerOrTeacher, IsEnrolledStudent

class AssignmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows assignments to be viewed or edited.
    - Teachers can create/edit assignments for their courses.
    - Students can view assignments for their enrolled courses.
    """
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated, IsTeacherOfCourse]

    def get_queryset(self):
        user = self.request.user
        queryset = Assignment.objects.all()

        # Filter by course if 'course' query param is provided
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        # Further restrict to user's courses if not staff/superuser
        if not (user.is_staff or user.is_superuser):
            teacher_courses = user.teaching_courses.all()
            student_courses = user.enrolled_courses.all()
            queryset = queryset.filter(
                Q(course__in=teacher_courses) | Q(course__in=student_courses)
            ).distinct()
            
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        show_answers = False

        if user.role == 'teacher' or user.is_staff or user.is_superuser:
            show_answers = True
        elif user.role == 'student':
            # Show answers if the student has a graded submission or if the due date has passed
            has_graded_submission = Submission.objects.filter(assignment=instance, student=user, status='graded').exists()
            is_past_due = instance.due_date and timezone.now() > instance.due_date
            if has_graded_submission or is_past_due:
                show_answers = True
        
        context = self.get_serializer_context()
        context['show_answers'] = show_answers
        
        serializer = self.get_serializer(instance, context=context)
        return Response(serializer.data)

class SubmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for handling assignment submissions.
    - Students can create submissions for assignments in their enrolled courses.
    - Students can view their own submissions.
    - Teachers can view and grade submissions for their courses.
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsEnrolledStudent]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'grade']:
            self.permission_classes = [IsAuthenticated, IsSubmissionOwnerOrTeacher]
        else: # list action
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        
        # Start with a base queryset based on user role
        if user.is_staff or user.is_superuser:
            queryset = Submission.objects.all()
        elif user.role == 'student':
            queryset = Submission.objects.filter(student=user)
        elif user.role == 'teacher':
            teacher_courses = user.teaching_courses.all()
            queryset = Submission.objects.filter(assignment__course__in=teacher_courses)
        else:
            queryset = Submission.objects.none()

        # Further filter by assignment if the 'assignment' query param is provided
        assignment_id = self.request.query_params.get('assignment')
        if assignment_id:
            queryset = queryset.filter(assignment_id=assignment_id)
            
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # This will call the serializer's create method and save the submission and answers
        submission = serializer.save(student=self.request.user)

        total_score = 0
        has_manual_grading = False

        for answer in submission.answers.all():
            question = answer.question
            is_correct = False

            if question.question_type == 'single_choice':
                correct_choice = question.choices.filter(is_correct=True).first()
                if correct_choice and answer.text == str(correct_choice.id):
                    is_correct = True
            
            elif question.question_type == 'multiple_choice':
                try:
                    # Frontend sends a sorted JSON array of strings
                    student_answer_ids = json.loads(answer.text) 
                    correct_choice_ids = sorted([str(pk) for pk in question.choices.filter(is_correct=True).values_list('id', flat=True)])
                    
                    if isinstance(student_answer_ids, list) and student_answer_ids == correct_choice_ids:
                        is_correct = True
                except (json.JSONDecodeError, TypeError):
                    is_correct = False

            elif question.question_type == 'true_false' or question.question_type == 'fill_in_the_blank':
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
        if has_manual_grading:
            submission.status = 'submitted'
        else:
            submission.status = 'graded'
        
        submission.save()

        # Re-serialize to return the updated data
        response_serializer = self.get_serializer(submission)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], url_path='grade')
    def grade(self, request, pk=None):
        submission = self.get_object()
        
        if request.user.role != 'teacher' or request.user != submission.assignment.course.teacher:
            return Response({'detail': 'You do not have permission to grade this submission.'}, status=status.HTTP_403_FORBIDDEN)

        answers_data = request.data.get('answers', [])
        feedback = request.data.get('feedback')

        total_score = 0
        for answer_data in answers_data:
            try:
                answer = Answer.objects.get(id=answer_data['id'], submission=submission)
                score = answer_data.get('score', 0)
                # Ensure score does not exceed question points
                if score > answer.question.points:
                    score = answer.question.points
                answer.score = score
                answer.save()
                total_score += score
            except (Answer.DoesNotExist, KeyError):
                # Silently ignore if answer not found or data is malformed
                continue

        submission.grade = total_score
        submission.feedback = feedback
        submission.status = 'graded'
        submission.save()

        serializer = self.get_serializer(submission)
        return Response(serializer.data, status=status.HTTP_200_OK)
