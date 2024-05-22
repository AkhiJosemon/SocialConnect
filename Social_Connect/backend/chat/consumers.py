from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .serialziers import *
from accounts.serializers import *
from django.utils.timesince import timesince
from asgiref.sync import sync_to_async
from .models import *

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        await self.channel_layer.group_add(self.room_group_name,self.channel_name)

        await self.accept()
        self.send(text_data= json.dumps({'status':'connected'}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name,self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user']
        user_serializer= userserializer(user)
        email = user_serializer.data['email']

        new_message = await self.create_message(self.room_id,message,email)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type'          :   'chat_message',
                'message'       :   message,
                'room_id'       :   self.room_id,
                'sender_email'  :   email,    
                'created'       :   timesince(new_message.created_at),
            }
            )
        
    async def chat_message(self,event):
        message = event['message']
        room_id = event['room_id']
        email   = event['sender_email']
        created = event['created']

        await self.send(text_data=json.dumps({
            'type':'chat_message',
            'message':message,
            'room_id':room_id,
            'sender_email':email,
            'created':created,
        }))


    @sync_to_async
    def create_message(self,room_id,message,email):
        user = User.objects.get(email=email)
        room = Room.objects.get(id=room_id)
        message = Message.objects.create(text=message,room=room,sender=user)
        message.save()
        return message

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Handle the received message here

        await self.send(text_data=json.dumps({
            'message': message
        }))



class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
        else:
            await self.accept()
            await self.channel_layer.group_add(
                f'notifications_{self.user.id}',
                self.channel_name
            )

    async def disconnect(self, close_code):
        if not self.user.is_anonymous:
            await self.channel_layer.group_discard(
                f'notifications_{self.user.id}',
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')

        # Handle received messages if needed

        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def send_notification(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))