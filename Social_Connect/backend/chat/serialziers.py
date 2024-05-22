from rest_framework import serializers
from accounts.models import  User 
from .models import *
from django.utils.timesince import timesince
from accounts.serializers import userserializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ 'id' , 'email' , 'first_name' , 'last_name' , 'username' , 'display_pic' ]

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    created = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = Message
        fields = '__all__'

    def get_created(self,obj):
        return timesince(obj.created_at)
    
class RoomListSerializer(serializers.ModelSerializer):
    get_unseen_message_count = serializers.SerializerMethodField()
    members = UserSerializer(many= True)

    class Meta:
        model= Room
        fields= '__all__'

    def get_unseen_message_count(self,obj):
        user =  self.context['request'].user
        return Message.objects.filter(room= obj,seen=False).exclude(sender=user).count()

    def to_representation(self, instance):
        user = self.context['request'].user
        members = instance.members.exclude(id=user.id)
        data = super(RoomListSerializer,self).to_representation(instance)
        data['members'] = UserSerializer(members,many=True).data
        return data
    

    def to_representation(self, instance):
        data = super(RoomListSerializer, self).to_representation(instance)
        members = instance.members.exclude(id=self.context['request'].user.id)
        data['members'] = userserializer(members, many=True, context=self.context).data
        return data

