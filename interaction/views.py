import random
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import DiscussionTopic, DiscussionReply, RandomQuestion, Vote, VoteChoice, VoteResponse
from .serializers import DiscussionTopicSerializer, DiscussionReplySerializer, RandomQuestionSerializer, VoteSerializer, VoteResponseSerializer, RandomQuestionDetailSerializer
from courses.permissions import IsCourseMember, IsAuthorOrTeacherOrReadOnly, IsCourseTeacher
from django.db.models import Q
from courses.models import Course
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

class DiscussionTopicListCreateView(generics.ListCreateAPIView):
    serializer_class = DiscussionTopicSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseMember]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        queryset = DiscussionTopic.objects.filter(course_id=course_id)

        # Search filter
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))

        # Date range filter
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, course_id=self.kwargs['course_id'])

class DiscussionTopicDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DiscussionTopicSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseMember, IsAuthorOrTeacherOrReadOnly]
    queryset = DiscussionTopic.objects.all()
    lookup_url_kwarg = 'topic_id'

class DiscussionReplyListCreateView(generics.ListCreateAPIView):
    serializer_class = DiscussionReplySerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseMember]

    def get_queryset(self):
        topic_id = self.kwargs['topic_id']
        return DiscussionReply.objects.filter(topic_id=topic_id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, topic_id=self.kwargs['topic_id'])

class MyDiscussionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Topics created by the user
        my_topics = DiscussionTopic.objects.filter(author=request.user).order_by('-created_at')
        my_topics_serializer = DiscussionTopicSerializer(my_topics, many=True)

        # Topics the user has replied to
        replied_topic_ids = DiscussionReply.objects.filter(author=request.user).values_list('topic_id', flat=True).distinct()
        replied_topics = DiscussionTopic.objects.filter(id__in=replied_topic_ids).order_by('-created_at')
        replied_topics_serializer = DiscussionTopicSerializer(replied_topics, many=True)


        return Response({
            'my_topics': my_topics_serializer.data,
            'replied_topics': replied_topics_serializer.data
        })


class RandomQuestionDetailView(generics.RetrieveDestroyAPIView):
    queryset = RandomQuestion.objects.all()
    serializer_class = RandomQuestionDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseMember]

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(
            queryset,
            course_id=self.kwargs['course_pk'],
            pk=self.kwargs['question_pk']
        )
        self.check_object_permissions(self.request, obj.course)
        return obj

class RandomQuestionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, IsCourseTeacher]

    def create(self, request, course_pk=None):
        course = get_object_or_404(Course, pk=course_pk)
        # Create a new random question instance without a student
        random_question = RandomQuestion.objects.create(course=course, status='ongoing')
        serializer = RandomQuestionSerializer(random_question, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsCourseTeacher])
    def draw(self, request, pk=None, course_pk=None):
        random_question = get_object_or_404(RandomQuestion, pk=pk, course_id=course_pk)
        if random_question.status == 'finished':
            return Response({"error": "This random question has already been finished."}, status=status.HTTP_400_BAD_REQUEST)

        course = random_question.course
        students = list(course.students.all())
        if not students:
            return Response({"error": "No students in this course to draw from."}, status=status.HTTP_400_BAD_REQUEST)

        random_student = random.choice(students)
        random_question.student = random_student
        random_question.status = 'finished'
        random_question.save()

        serializer = RandomQuestionDetailSerializer(random_question)
        return Response(serializer.data)

    def destroy(self, request, pk=None, course_pk=None):
        random_question = get_object_or_404(RandomQuestion, pk=pk, course_id=course_pk)
        random_question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VoteViewSet(viewsets.ModelViewSet):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseMember]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        course_id = self.kwargs['course_pk']
        return Vote.objects.filter(course_id=course_id).order_by('-created_at')

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            self.permission_classes = [permissions.IsAuthenticated, IsCourseTeacher]
        else:
            self.permission_classes = [permissions.IsAuthenticated, IsCourseMember]
        return super().get_permissions()

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        serializer.save(course=course)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsCourseMember])
    def vote(self, request, pk=None, course_pk=None):
        vote = self.get_object()
        choice_id = request.data.get('choice_id')

        if not choice_id:
            return Response({'error': 'Choice ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            choice = VoteChoice.objects.get(id=choice_id, vote=vote)
        except VoteChoice.DoesNotExist:
            return Response({'error': 'Invalid choice.'}, status=status.HTTP_400_BAD_REQUEST)

        student = request.user

        try:
            # The unique_together constraint on ('vote', 'student') will prevent multiple votes.
            response = VoteResponse.objects.create(vote=vote, choice=choice, student=student)
            serializer = VoteResponseSerializer(response)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'error': 'You have already voted in this poll.'}, status=status.HTTP_400_BAD_REQUEST)
