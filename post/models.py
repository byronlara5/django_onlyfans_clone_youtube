from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from tier.models import Tier, Subscription
from notifications.models import Notification
# Create your models here.
def user_directory_path(instance, filename):
    #This file will be uploaded to MEDIA_ROOT /the user(id)/thefile
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class PostFileContent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_owner')
    file = models.FileField(upload_to=user_directory_path)
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, related_name='tier_file')
    posted = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.ManyToManyField(PostFileContent, related_name='contents')
    title = models.CharField(max_length=150)
    caption = models.TextField(max_length=1500, verbose_name='Caption')
    posted = models.DateTimeField(auto_now_add=True)
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, related_name='tiers')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    favorites_count = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse('postdetails', args=[str(self.id)])

class Stream(models.Model):
    subscribed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stream_subscribed')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    visible = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    @receiver(post_save, sender=Post, dispatch_uid='unique_add_post')
    def add_post(sender, instance, created, **kwargs):
        post = instance
        user = post.user

        if created:
            subscribers = Subscription.objects.all().filter(subscribed=user)
            for subscriber in subscribers:
                if(subscriber.tier.number >= post.tier.number):
                    stream = Stream(post=post, user=subscriber.subscriber, date=post.posted, subscribed=user, visible=True)
                    stream.save()
                else:
                    stream = Stream(post=post, user=subscriber.subscriber, date=post.posted, subscribed=user)
                    stream.save()

class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
     
    def user_liked_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user
        notify = Notification(post=post, sender=sender, user=post.user, notification_type=1)
        notify.save()
    def user_unlike_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user
        notify = Notification.objects.filter(post=post, sender=sender, notification_type=1)
        notify.delete()

class Bookmark(models.Model):
    posts = models.ManyToManyField(Post)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmark_user')

#Signals stuff for Likes:
post_save.connect(Likes.user_liked_post, sender=Likes)
post_delete.connect(Likes.user_unlike_post, sender=Likes)