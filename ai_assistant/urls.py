from django.urls import path
from .views import (
    ChatSessionListCreateView,
    ChatMessageListCreateView,
    ChatSessionRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('sessions/', ChatSessionListCreateView.as_view(), name='chat-session-list'),
    path('sessions/<int:session_id>/', ChatSessionRetrieveUpdateDestroyView.as_view(), name='chat-session-detail'),
    path('sessions/<int:session_id>/messages/', ChatMessageListCreateView.as_view(), name='chat-message-list'),
]
