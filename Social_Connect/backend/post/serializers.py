from rest_framework import serializers
from .models import Posts,Follow,Comment
from accounts.models import User
from accounts.serializers import userserializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'display_pic')

class ImagePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['description', 'img']  # Specify fields to include in the serializer

class PostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['id', 'author','description', 'img', 'likes', 'created_at', 'updated_at', 'is_deleted', 'is_blocked']


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model =Follow
        fields = '__all__' 
        

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    created_time = serializers.CharField()
    
    class Meta:
        model = Comment
        fields = ('id', 'post', 'user', 'body', 'created_at', 'created_time')

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    created_time = serializers.CharField()  # Remove source='created_time'
    
    author = UserSerializer() 
    class Meta:
        model = Posts
        fields = ('id', 'description', 'author', 'img', 'likes', 'video', 'created_at', 'updated_at', 'is_deleted', 'is_blocked', 'reported_users', 'total_likes', 'created_time', 'comments')

class FollowingDetails(serializers.ModelSerializer):
    following_user = userserializer(source='following', read_only=True)
    class Meta:
        model = Follow
        fields = ('__all__')