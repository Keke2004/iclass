from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import DiscussionTopic, DiscussionReply
from .serializers import DiscussionTopicSerializer, DiscussionReplySerializer
from courses.permissions import IsCourseMember, IsAuthorOrTeacherOrReadOnly
from django.db.models import Q

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
