from django.urls import path
from .views import CreateImagePost,UserPosts,follow,followDetails,followersPost,postDetails,unFollow,likePost,LikeDetails,CommentView,TotalCountsView,followingsView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('create-post/', CreateImagePost.as_view(), name='create-post'),
    path('get-post-profile/',UserPosts.as_view(),name='get-post-profile'),
    path('follow-user/',follow.as_view(),name='follow-user'),
    path('follow-details/',followDetails.as_view(),name='follow-user'),
    path('following-post/',followersPost.as_view(),name='following-post'),
    path('post-details/<int:post_id>/',postDetails.as_view(),name='post-details'),
    path('unfollow-user/<int:id>/',unFollow.as_view(),name='unfollow-user'),
    path('like/<int:id>/',likePost.as_view(),name='like'),
    path('like-details/<int:id>/',LikeDetails.as_view(),name='like-details'),
    path('comment/<int:id>/',CommentView.as_view(),name='Comment'),
    path('total-counts/<int:id>/',TotalCountsView.as_view(),name='total-counts'),
    path('followings/',followingsView.as_view(),name='followings')


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)