from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import requests
import os
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer

class ChatSessionListCreateView(generics.ListCreateAPIView):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ChatSessionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'session_id'

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

class ChatMessageListCreateView(generics.ListCreateAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        session_id = self.kwargs.get('session_id')
        return self.queryset.filter(session__user=self.request.user, session_id=session_id).order_by('created_at')

    def create(self, request, *args, **kwargs):
        session_id = self.kwargs.get('session_id')
        question = request.data.get('content')
        model = request.data.get('model', 'xiaomi/mimo-v2-flash:free') # Default model

        if not question:
            return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({"error": "Chat session not found"}, status=status.HTTP_404_NOT_FOUND)

        # Save user message
        user_message = ChatMessage.objects.create(session=session, content=question, is_from_user=True)

        # Prepare context for AI
        history = ChatMessage.objects.filter(session=session).order_by('created_at')
        messages_for_ai = [{"role": "user" if msg.is_from_user else "assistant", "content": msg.content} for msg in history]

        api_key = os.environ.get("OPENROUTER_API_KEY", "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")
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:5173",
                    "X-Title": "iClass",
                },
                json={
                    "model": model,
                    "messages": messages_for_ai
                }
            )
            response.raise_for_status()
            
            data = response.json()
            answer = data['choices'][0]['message']['content']
            
            # Save AI message
            ai_message = ChatMessage.objects.create(session=session, content=answer, is_from_user=False)

            # If session topic is empty, set it with the first question
            if not session.topic:
                session.topic = question[:60] # Truncate to 60 chars
                session.save()
            
            serializer = self.get_serializer(ai_message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
