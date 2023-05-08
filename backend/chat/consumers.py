import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message,Room
from django.shortcuts import get_object_or_404


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = "chat_%s" % self.room_id 
            
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        command = text_data_json["command"]
        await self.commands[command](self, text_data_json or None)
    
    # loads all saved messages on connection
    async def load_messages(self,x):
        room_id = self.scope['url_route']["kwargs"]['room_id']
        msgs = await self.room_msgs_to_list(room_id)

        #for-loop for sending room messaes on chatsocket connection         
        for msg in msgs:
            await self.channel_layer.group_send(
            self.room_group_name, {
            "type": "chat_message", "message": msg['message'],
            'author' : msg['author'], 'timestamp': msg['timestamp']                    
            })
    
    async def new_message(self,text_data_json):
        
        if self.scope['user'].is_authenticated:  
            msg = await self.create_msg(
                content = text_data_json['message'],
                author = self.scope['user'],
                room_id = self.scope['url_route']["kwargs"]['room_id']
            )
        else:
            msg = await self.anon_create_msg(
                content = text_data_json['message'],
                author_name = self.scope['session']['dp_name'],
                room_id = self.scope['url_route']["kwargs"]['room_id']
            )
            
        await self.channel_layer.group_send(
            self.room_group_name, {
            "type": "chat_message", "message": msg.content,
             'author':msg.author_name, 'timestamp': msg.created_on                    
            }
        )
    
    # command dictionary for calling functions 
    commands = {
        'new_message': new_message,
        'load_messages': load_messages
    }
    
    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        author = event["author"]
        timestamp = event["timestamp"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": message, 'author':author, 'timestamp':timestamp
        }))

    # create database msg for authenticated users
    @database_sync_to_async
    def create_msg(self,content,author,room_id):
        room = get_object_or_404(Room,room_id=room_id)
        msg= Message.objects.create(
            content=content, author=author
        )
        room.messages.add(msg)
        return msg
    
    # create database msg for anonymous users
    @database_sync_to_async
    def anon_create_msg(self,content,author_name,room_id):
        room = get_object_or_404(Room,room_id=room_id)
        msg= Message.objects.create(
            content=content, display_name=author_name
        )
        room.messages.add(msg)
        return msg
    
    @database_sync_to_async
    def room_msgs_to_list(self,room_id):
        room = get_object_or_404(Room,room_id=room_id)
        msgs = [
            {'message':msg.content,'author':msg.author_name,'timestamp':msg.created_on}
            for msg in room.messages.all()
        ]
        return msgs
