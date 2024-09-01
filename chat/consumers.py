import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, Message, User
from django.core.exceptions import ObjectDoesNotExist

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        '''
        Called when the websocket is handshaking as part of initial connection.
        
        '''
        self.user = self.scope["user"]

        # Check if user is authenticated
        if self.user.is_anonymous:
            await self.close()
            return

        # Extract the other user ID from the URL
        user2_id = self.scope['url_route']['kwargs'].get('user2_id')
        if not user2_id:
            await self.close()
            return

        try:
            user2 = await database_sync_to_async(User.objects.get)(id=user2_id)
        except User.DoesNotExist:
            await self.close()
            return

        # Generate or retrieve a unique chat ID
        self.room_name = self.get_chat_id(self.user.id, user2_id)
        self.room_group_name = f"chat_{self.room_name}"

        # Ensure chat exists or create it with both users as participants
        await self.ensure_chat_exists(self.user, user2)

        # Check if the user is part of the chat
        chat_exists = await self.check_user_in_chat(self.user, self.room_name)
        if not chat_exists:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Load last 25 messages from Redis
        previous_messages = await self.get_last_25_messages()

        # Send previous messages to the WebSocket
        for message in previous_messages:
            await self.send(text_data=json.dumps({
                'message': message
            }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Check if the user is part of the chat before saving
        chat_exists = await self.check_user_in_chat(self.user, self.room_name)
        if not chat_exists:
            await self.close()
            return

        # Save message to the database synchronously
        await database_sync_to_async(self.save_message)(self.room_name, self.user, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Store message in Redis
        await self.store_message_in_redis(message)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def save_message(self, chat_id, user, message):
        """Synchronously save message to the database."""
        chat = Chat.objects.get(id=chat_id)
        Message.objects.create(chat=chat, sender=user, content=message)

    async def store_message_in_redis(self, message):
        """Store message in Redis, limiting to the last 25 messages."""
        # Store message in the Redis list for the chat room
        await self.channel_layer.redis_instance.lpush(self.room_group_name, message)
        # Trim list to only keep the last 25 messages
        await self.channel_layer.redis_instance.ltrim(self.room_group_name, 0, 24)

    async def get_last_25_messages(self):
        """Retrieve the last 25 messages from Redis."""
        # Fetch the last 25 messages from Redis
        messages = await self.channel_layer.redis_instance.lrange(self.room_group_name, 0, 24)
        return [message.decode('utf-8') for message in messages]

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
        # Generate a unique chat ID
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
