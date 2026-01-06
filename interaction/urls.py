from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DiscussionTopicListCreateView,
    DiscussionTopicDetailView,
    DiscussionReplyListCreateView,
    MyDiscussionsView,
    VoteViewSet,
    RandomQuestionViewSet,
    RandomQuestionDetailView,
)

router = DefaultRouter()
router.register(r'courses/(?P<course_pk>\d+)/votes', VoteViewSet, basename='vote')
router.register(r'courses/(?P<course_pk>\d+)/random-questions', RandomQuestionViewSet, basename='random-question')


urlpatterns = [
    path('courses/<int:course_id>/discussions/', DiscussionTopicListCreateView.as_view(), name='discussion-list-create'),
    path('courses/<int:course_id>/discussions/<int:topic_id>/', DiscussionTopicDetailView.as_view(), name='discussion-detail'),
    path('courses/<int:course_id>/discussions/<int:topic_id>/replies/', DiscussionReplyListCreateView.as_view(), name='reply-list-create'),
    path('mydiscussions/', MyDiscussionsView.as_view(), name='my-discussions'),
    path('courses/<int:course_pk>/random-questions/<int:question_pk>/', RandomQuestionDetailView.as_view(), name='random-question-detail'),
    path('', include(router.urls)),
]
