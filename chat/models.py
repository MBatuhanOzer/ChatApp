from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        participants_names = ', '.join(user.username for user in self.participants.all())
        return f"Chat between {participants_names}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} in chat {self.chat.id}"

    class Meta:
        ordering = ('timestamp',)
