from django.urls import path
from .views import (
    DiscussionTopicListCreateView,
    DiscussionTopicDetailView,
    DiscussionReplyListCreateView,
    MyDiscussionsView,
)

urlpatterns = [
    path('courses/<int:course_id>/discussions/', DiscussionTopicListCreateView.as_view(), name='discussion-list-create'),
    path('courses/<int:course_id>/discussions/<int:topic_id>/', DiscussionTopicDetailView.as_view(), name='discussion-detail'),
    path('courses/<int:course_id>/discussions/<int:topic_id>/replies/', DiscussionReplyListCreateView.as_view(), name='reply-list-create'),
    path('mydiscussions/', MyDiscussionsView.as_view(), name='my-discussions'),
]
