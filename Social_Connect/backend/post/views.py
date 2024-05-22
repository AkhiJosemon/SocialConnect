from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Posts,Follow,Comment
from .serializers import ImagePostSerializer,PostsSerializer,FollowSerializer,PostSerializer,FollowingDetails
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from accounts.models import User
from accounts.serializers import AllUserSerializer
from django.http import JsonResponse
from django.utils import timezone
from django.core import serializers

class CreateImagePost(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, *args, **kwargs):
        print("in")
        
        serializer = ImagePostSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.validated_data['author'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPosts(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        print("inside userpost")
        user=request.GET.get('user_id')
        user_posts = Posts.objects.filter(author_id=user)
        serializer = PostsSerializer(user_posts, many=True)
        return Response(serializer.data)

class follow(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        print("inside follow")

        user=request.user
        print(user)
        follows= request.data.get('following_id')
        follow_user = User.objects.get(pk=follows)
        
        is_following = Follow.objects.filter(follower = user , following = follow_user )
        if is_following:
            is_following.delete()
            response_msg = 'Unfollowed Successfully'

        else:
            new_follow = Follow(follower = user ,following = follow_user)
            new_follow.save()
 
            response_msg = 'Followed Successfully'
        return Response({
              'message' : response_msg  
            },status=status.HTTP_200_OK)
        

    
class followDetails(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        user= request.user
        print("followDetails")
        followers = Follow.objects.filter(following=user)
        following= Follow.objects.filter(follower=user)


       
        followers_serializer=FollowSerializer(followers, many=True)
        following_serializer=FollowSerializer(following, many=True)
        print(followers,following)

        
        return Response({
            'followers' : followers_serializer.data,
            'following' : following_serializer.data
        },status=status.HTTP_200_OK)
        
class followersPost(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        following = Follow.objects.filter(follower=user)
        posts_data = []

        for follow_obj in following:
            second_user = follow_obj.following  # Get the second user
            second_user_posts = second_user.posts.all().order_by('-created_at')  # Retrieve posts of the second user
            user_data = AllUserSerializer(second_user).data
            user_posts_data = PostsSerializer(second_user_posts, many=True).data
            
            for post_data in user_posts_data:
                post_data_with_author = {
                    'author_first_name': user_data['first_name'],
                    'author_display_pic': user_data['display_pic'],
                    
                    
                    **post_data  # Include all other post data
                }
                posts_data.append(post_data_with_author)

        # Sort posts_data by 'created_at' field
        sorted_posts_data = sorted(posts_data, key=lambda x: x['created_at'], reverse=True)
        print(sorted_posts_data)
        return Response(sorted_posts_data)


class postDetails(APIView):
    permimission_classes = [IsAuthenticated]
    def get(self ,request,post_id):
        print("inside postDetails")
        
        post = Posts.objects.get(pk=post_id)
        print(post)
        serializer = PostSerializer(post)
        print("all postdetails data",serializer.data)
        return Response(serializer.data,status=status.HTTP_200_OK)

class unFollow(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request,id):
        print(id)
        following_id=id
        following_user = get_object_or_404(User, id=following_id)
        follow_instance = Follow.objects.filter(follower=request.user, following=following_user)
        print("going to unfollow")
        follow_instance.delete()
        return JsonResponse({'message': 'User unfollowed successfully.'}, status=status.HTTP_200_OK)
    

class likePost(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request,id):
        print("likepost")
        post= get_object_or_404(Posts , pk=id)

        if request.user in post.likes.all():

            post.likes.remove(request.user)
            liked = False
        
        else:
            post.likes.add(request.user)
            liked = True

        post.save()

        return JsonResponse({'liked':liked},status=status.HTTP_200_OK) 
    
class LikeDetails(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,id):
        post = get_object_or_404(Posts, pk=id)
        if request.user in post.likes.all():
            liked = True
        else:
            liked = False

        return JsonResponse({ 'liked' : liked },status=status.HTTP_200_OK)
    

class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        print("inside Comment")
        post = get_object_or_404(Posts, pk=id)
        user = request.user
        comment_body = request.data.get('body')  # Access POST data correctly
        print(comment_body)

        if not comment_body:
            return Response({"error": "Comment body is required"}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(
            post=post,
            user=user,
            body=comment_body,
            created_at=timezone.now()
        )

        # Save the Comment object
        comment.save()
        return Response(status=status.HTTP_200_OK)


class TotalCountsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,id):
        user_id=id
        user=User.objects.get(pk=user_id)
        post_details=Posts.objects.filter(author=user)
        post_count = post_details.count()
        followers=Follow.objects.filter(following=user)
        followers_count = followers.count()
        following=Follow.objects.filter(follower=user)
        following_count=following.count()


        serialized_followers = serializers.serialize('json', followers)
        serialized_following = serializers.serialize('json', following)

        data = {
                'post_count': post_count,
                'followers_count': followers_count,
                'following_count': following_count,
                
                'followers': serialized_followers,
                'following': serialized_following,
                }
        
        return JsonResponse(data,status=status.HTTP_200_OK)
    

class followingsView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self,request):
        
        following=Follow.objects.filter(follower=request.user)
        serialized=FollowingDetails(following,many=True)

        return Response(serialized.data,status=status.HTTP_200_OK)