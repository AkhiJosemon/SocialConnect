from django.db import models
from accounts.models import User
from django.utils.timesince import timesince


# Create your models here.

class Posts(models.Model):
    description =models.TextField(blank=True,null=True)
    author =models.ForeignKey(User,related_name='posts',on_delete=models.CASCADE)
    img = models.ImageField(upload_to='posts/')
    likes = models.ManyToManyField(User,related_name='liked_posts',blank=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked=models.BooleanField(default=False)
    reported_users =models.ManyToManyField(User,related_name='reported_posts',blank=True)
    

    def __str__(self):
        return self.author.username
    
    def total_likes(self):
        return self.likes.count() 
    
    
    def created_time(self):
        return timesince(self.created_at)
    



class Comment(models.Model):
    post = models.ForeignKey(Posts,related_name='comments',on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    body=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return '%s - %s - %s' % (self.post.id,self.body,self.user.first_name)
    
    def created_time(self):
        return timesince(self.created_at)
        
   
class Follow(models.Model):
    follower = models.ForeignKey(User,related_name='followers',on_delete=models.CASCADE)
    following = models.ForeignKey(User,related_name='following',on_delete=models.CASCADE)
    
    def __str__(self) :
        return f'{self.follower} -> {self.following}'   
    

class ReportedPost(models.Model):
    post_id=models.ForeignKey(Posts,related_name='ReportedPost',on_delete=models.CASCADE)
    reason=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.post_id
    