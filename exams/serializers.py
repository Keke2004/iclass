from rest_framework import serializers
from django.utils import timezone
from .models import Exam, ExamQuestion, ExamChoice, ExamSubmission, ExamAnswer
from users.models import User

class StudentExamSubmissionStatusSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    student_id = serializers.IntegerField(source='student.id', read_only=True)

    class Meta:
        model = ExamSubmission
        fields = ['id', 'student_id', 'student_name', 'status', 'grade']

class ExamChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamChoice
        fields = ['id', 'text', 'is_correct']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        show_answers = self.context.get('show_answers', False)
        if not show_answers:
            ret.pop('is_correct', None)
        return ret

class ExamQuestionSerializer(serializers.ModelSerializer):
    choices = ExamChoiceSerializer(many=True, required=False)

    class Meta:
        model = ExamQuestion
        fields = ['id', 'text', 'question_type', 'points', 'choices', 'correct_answer']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        show_answers = self.context.get('show_answers', False)
        if not show_answers:
            ret.pop('correct_answer', None)
        return ret

class ExamSerializer(serializers.ModelSerializer):
    questions = ExamQuestionSerializer(many=True)
    submission_stats = serializers.SerializerMethodField()
    student_submissions = serializers.SerializerMethodField()
    is_teacher = serializers.SerializerMethodField()
    submission = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ['id', 'course', 'title', 'description', 'start_time', 'end_time', 'time_limit', 'questions', 'submission_stats', 'student_submissions', 'is_teacher', 'submission']

    def get_is_teacher(self, obj):
        user = self.context['request'].user
        return obj.course.teacher == user

    def get_submission(self, obj):
        user = self.context['request'].user
        if user.is_authenticated and user.role == 'student':
            try:
                submission = ExamSubmission.objects.get(exam=obj, student=user)
                return ExamSubmissionSerializer(submission, context=self.context).data
            except ExamSubmission.DoesNotExist:
                return None
        return None

    def get_submission_stats(self, obj):
        if not self.get_is_teacher(obj):
            return None
        
        submissions = ExamSubmission.objects.filter(exam=obj)
        total_students = obj.course.students.count()
        
        # Count manually graded submissions
        manually_graded_count = submissions.filter(status='graded').count()
        
        # Count auto-graded (not submitted and past due date)
        auto_graded_count = 0
        if obj.end_time and timezone.now() > obj.end_time:
            submitted_student_ids = submissions.values_list('student_id', flat=True)
            not_submitted_count = obj.course.students.exclude(id__in=submitted_student_ids).count()
            auto_graded_count = not_submitted_count

        total_graded = manually_graded_count + auto_graded_count
        total_submissions = submissions.count() # This remains the count of actual submissions

        return {
            'total_students': total_students,
            'total_submissions': total_submissions,
            'graded_submissions': total_graded
        }

    def get_student_submissions(self, obj):
        if not self.get_is_teacher(obj):
            return []

        course_students = obj.course.students.all()
        submissions = ExamSubmission.objects.filter(exam=obj).select_related('student')
        
        submission_map = {sub.student.id: sub for sub in submissions}
        
        student_submission_statuses = []
        for student in course_students:
            submission = submission_map.get(student.id)
            if submission:
                student_submission_statuses.append({
                    'student_id': student.id,
                    'student_name': student.username,
                    'status': submission.status,
                    'submission_id': submission.id,
                    'grade': submission.grade
                })
            else:
                # Student has not submitted
                grade = None
                status = 'not_submitted'
                # If the due date has passed, mark as graded with 0 score
                if obj.end_time and timezone.now() > obj.end_time:
                    grade = 0
                    status = 'graded'

                student_submission_statuses.append({
                    'student_id': student.id,
                    'student_name': student.username,
                    'status': status,
                    'submission_id': None,
                    'grade': grade
                })
        return student_submission_statuses

    def to_internal_value(self, data):
        questions_data = data.get('questions', [])
        for question_data in questions_data:
            if question_data.get('question_type') not in ['single_choice', 'multiple_choice']:
                question_data.pop('choices', None)
        return super().to_internal_value(data)

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        exam = Exam.objects.create(**validated_data)
        for question_data in questions_data:
            choices_data = question_data.pop('choices', [])
            question = ExamQuestion.objects.create(exam=exam, **question_data)
            if question.question_type in ['single_choice', 'multiple_choice']:
                for choice_data in choices_data:
                    ExamChoice.objects.create(question=question, **choice_data)
        return exam

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)
        instance.time_limit = validated_data.get('time_limit', instance.time_limit)
        instance.save()

        if 'questions' in validated_data:
            questions_data = validated_data.get('questions', [])
            existing_questions = {q.id: q for q in instance.questions.all()}
            
            for q_data in questions_data:
                q_id = q_data.get('id')
                if q_id and q_id in existing_questions:
                    question = existing_questions.pop(q_id)
                    question.text = q_data.get('text', question.text)
                    question.question_type = q_data.get('question_type', question.question_type)
                    question.points = q_data.get('points', question.points)
                    question.correct_answer = q_data.get('correct_answer', question.correct_answer)
                    question.save()
                    
                    if question.question_type in ['single_choice', 'multiple_choice']:
                        choices_data = q_data.get('choices', [])
                        existing_choices = {c.id: c for c in question.choices.all()}
                        for c_data in choices_data:
                            c_id = c_data.get('id')
                            if c_id and c_id in existing_choices:
                                choice = existing_choices.pop(c_id)
                                choice.text = c_data.get('text', choice.text)
                                choice.is_correct = c_data.get('is_correct', choice.is_correct)
                                choice.save()
                            else:
                                ExamChoice.objects.create(question=question, **c_data)
                        # for choice in existing_choices.values():
                        #     choice.delete()

            # for question in existing_questions.values():
            #     question.delete()

        instance.refresh_from_db()
        return instance

class ExamAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAnswer
        fields = ['id', 'question', 'text', 'score']
        read_only_fields = ['score']

class ExamSubmissionSerializer(serializers.ModelSerializer):
    answers = ExamAnswerSerializer(many=True)
    student = serializers.StringRelatedField(read_only=True)
    student_id = serializers.IntegerField(source='student.id', read_only=True)

    class Meta:
        model = ExamSubmission
        fields = ['id', 'exam', 'student', 'student_id', 'start_time', 'submitted_at', 'grade', 'feedback', 'status', 'answers']
        read_only_fields = ['grade', 'feedback', 'status', 'start_time', 'submitted_at']

    def validate(self, data):
        exam = data.get('exam')
        request = self.context.get('request')

        if request and request.user.is_authenticated and request.user.role == 'student':
            if self.instance is None and exam.end_time and timezone.now() > exam.end_time:
                raise serializers.ValidationError("考试已过截止日期，无法提交。")
        
        return data

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        student = self.context['request'].user
        submission = ExamSubmission.objects.create(student=student, **validated_data)
        for answer_data in answers_data:
            ExamAnswer.objects.create(submission=submission, **answer_data)
        return submission
