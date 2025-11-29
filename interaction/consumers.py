import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Discussion, Course
from users.models import User
from channels.db import database_sync_to_async

class DiscussionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.course_id = self.scope['url_route']['kwargs']['course_id']
        self.course_group_name = f'chat_{self.course_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.course_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.course_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user_id = self.scope['user'].id

        if not user_id:
            return

        # Save message to database
        await self.save_message(user_id, self.course_id, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.course_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.scope['user'].username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @database_sync_to_async
    def save_message(self, user_id, course_id, message):
        user = User.objects.get(id=user_id)
        course = Course.objects.get(id=course_id)
        Discussion.objects.create(student=user, course=course, message=message)
