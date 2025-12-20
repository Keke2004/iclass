from rest_framework import serializers
from django.utils import timezone
from .models import Assignment, Question, Choice, Submission, Answer
from users.models import User

class StudentSubmissionStatusSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    student_id = serializers.IntegerField(source='student.id', read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'student_id', 'student_name', 'status', 'grade']

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']

    def to_representation(self, instance):
        # 动态决定是否显示 is_correct 字段
        ret = super().to_representation(instance)
        show_answers = self.context.get('show_answers', False)
        if not show_answers:
            ret.pop('is_correct', None)
        return ret

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'points', 'choices', 'correct_answer']

    def to_representation(self, instance):
        # 动态决定是否显示 correct_answer 字段
        ret = super().to_representation(instance)
        show_answers = self.context.get('show_answers', False)
        if not show_answers:
            ret.pop('correct_answer', None)
        return ret

class AssignmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    submission_stats = serializers.SerializerMethodField()
    student_submissions = serializers.SerializerMethodField()
    is_teacher = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ['id', 'course', 'title', 'description', 'due_date', 'questions', 'submission_stats', 'student_submissions', 'is_teacher']

    def get_is_teacher(self, obj):
        user = self.context['request'].user
        return obj.course.teacher == user

    def get_submission_stats(self, obj):
        if not self.get_is_teacher(obj):
            return None
        
        submissions = Submission.objects.filter(assignment=obj)
        total_students = obj.course.students.count()
        
        # Count manually graded submissions
        manually_graded_count = submissions.filter(status='graded').count()
        
        # Count auto-graded (not submitted and past due date)
        auto_graded_count = 0
        if obj.due_date and timezone.now() > obj.due_date:
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
        # This method is only relevant for teachers
        if not self.get_is_teacher(obj):
            return []

        course_students = obj.course.students.all()
        submissions = Submission.objects.filter(assignment=obj).select_related('student')
        
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
                if obj.due_date and timezone.now() > obj.due_date:
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
        # 在验证前处理数据
        questions_data = data.get('questions', [])
        for question_data in questions_data:
            # 如果问题类型不是单选或多选，则移除 choices 字段
            if question_data.get('question_type') not in ['single_choice', 'multiple_choice']:
                question_data.pop('choices', None)
        return super().to_internal_value(data)

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        assignment = Assignment.objects.create(**validated_data)
        for question_data in questions_data:
            choices_data = question_data.pop('choices', [])
            question = Question.objects.create(assignment=assignment, **question_data)
            if question.question_type in ['single_choice', 'multiple_choice']:
                for choice_data in choices_data:
                    Choice.objects.create(question=question, **choice_data)
        return assignment

    def update(self, instance, validated_data):
        # 更新作业基本信息
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.save()

        # 只有在请求中包含 questions 数据时才进行更新
        if 'questions' in validated_data:
            questions_data = validated_data.get('questions', [])
            existing_questions = {question.id: question for question in instance.questions.all()}
            
            for question_data in questions_data:
                question_id = question_data.get('id')
                if question_id and question_id in existing_questions:
                    # 更新现有问题
                    question = existing_questions.pop(question_id)
                    question.text = question_data.get('text', question.text)
                    question.question_type = question_data.get('question_type', question.question_type)
                    question.points = question_data.get('points', question.points)
                    question.correct_answer = question_data.get('correct_answer', question.correct_answer)
                    question.save()
                    
                    # 更新选项
                    if question.question_type in ['single_choice', 'multiple_choice']:
                        choices_data = question_data.get('choices', [])
                        existing_choices = {choice.id: choice for choice in question.choices.all()}
                        for choice_data in choices_data:
                            choice_id = choice_data.get('id')
                            if choice_id and choice_id in existing_choices:
                                choice = existing_choices.pop(choice_id)
                                choice.text = choice_data.get('text', choice.text)
                                choice.is_correct = choice_data.get('is_correct', choice.is_correct)
                                choice.save()
                            else:
                                Choice.objects.create(question=question, **choice_data)
                        # # 删除不再存在的选项 (暂时禁用以防止意外删除)
                        # for choice in existing_choices.values():
                        #     choice.delete()

            # # 删除不再存在的问题 (暂时禁用以防止意外删除)
            # for question in existing_questions.values():
            #     question.delete()

        instance.refresh_from_db()
        return instance

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'text', 'score']
        read_only_fields = ['score']

class SubmissionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    student = serializers.StringRelatedField(read_only=True)
    student_id = serializers.IntegerField(source='student.id', read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'assignment', 'student', 'student_id', 'submitted_at', 'grade', 'feedback', 'status', 'answers']
        read_only_fields = ['grade', 'feedback', 'status']

    def validate(self, data):
        assignment = data.get('assignment')
        request = self.context.get('request')

        # This validation should only apply to students creating a new submission.
        if request and request.user.is_authenticated and request.user.role == 'student':
            # self.instance is None for a 'create' operation.
            if self.instance is None and assignment.due_date and timezone.now() > assignment.due_date:
                raise serializers.ValidationError("作业已过截止日期，无法提交。")
        
        return data

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        submission = Submission.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(submission=submission, **answer_data)
        return submission
