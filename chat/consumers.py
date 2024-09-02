import json
import redis
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from .models import Chat, Message, User

# Create a Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)  # Update Redis configuration if necessary

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        user2_id = self.scope['url_route']['kwargs'].get('user2_id')
        if not user2_id:
            await self.close()
            return

        try:
            user2 = await database_sync_to_async(User.objects.get)(id=user2_id)
        except User.DoesNotExist:
            await self.close()
            return

        self.room_name = self.get_chat_id(self.user.id, user2_id)
        self.room_group_name = f"chat_{self.room_name}"

        await self.ensure_chat_exists(self.user, user2)

        chat_exists = await self.check_user_in_chat(self.user, self.room_name)
        if not chat_exists:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Load last 25 messages from Redis in the correct order
        previous_messages = await self.get_last_25_messages()

        # Send previous messages to the WebSocket
        for message in reversed(previous_messages):  # Reverse to maintain correct order
            await self.send(text_data=json.dumps(message))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']

        chat_exists = await self.check_user_in_chat(self.user, self.room_name)
        if not chat_exists:
            await self.close()
            return

        await self.save_message(self.room_name, self.user, message_content)

        message = {
            'type': 'chat_message',
            'message': message_content,
            'sender_id': self.user.id,
            'sender_username': self.user.username
        }

        await self.store_message_in_redis(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            message
        )

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        sender_username = event['sender_username']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'sender_username': sender_username
        }))

    @database_sync_to_async
    def save_message(self, chat_id, user, message):
        """Synchronously save message to the database."""
        chat = Chat.objects.get(id=chat_id)
        Message.objects.create(chat=chat, sender=user, content=message)

    async def store_message_in_redis(self, message):
        """Store message in Redis, including sender information."""
        redis_client.lpush(self.room_group_name, json.dumps(message))
        redis_client.ltrim(self.room_group_name, 0, 24)

    async def get_last_25_messages(self):
        """Retrieve the last 25 messages from Redis."""
        # Fetch the last 25 messages from Redis
        messages = redis_client.lrange(self.room_group_name, 0, 24)
    
        decoded_messages = []
        for message in messages:
            try:
                # Check if the message is not empty before decoding
                if message:
                    decoded_message = json.loads(message.decode('utf-8'))
                    decoded_messages.append(decoded_message)
            except json.JSONDecodeError:
                # Log the error or handle it as needed
                print("Invalid JSON data found in Redis, skipping entry.")
                continue
    
        return decoded_messages


    @database_sync_to_async
    def check_user_in_chat(self, user, chat_id):
        """Check if the user is part of the chat."""
        try:
            chat = Chat.objects.get(id=chat_id)
            return chat.participants.filter(id=user.id).exists()
        except Chat.DoesNotExist:
            return False

    @database_sync_to_async
    def ensure_chat_exists(self, user1, user2):
        """Ensure that a chat exists between the participants. Create if not."""
        chat = Chat.objects.filter(participants__id=user1.id).filter(participants__id=user2.id).first()
        if not chat:
            chat_id = self.get_chat_id(user1.id, user2.id)
            chat = Chat(id=chat_id)
            chat.save()
            chat.participants.add(user1, user2)
            chat.save()

    @staticmethod
    def get_chat_id(user1_id, user2_id):
        """Generate a unique chat ID based on user IDs."""
        return f"{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"
