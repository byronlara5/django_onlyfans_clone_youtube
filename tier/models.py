from django.db import models

from notifications.models import Notification
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete

# Create your models here.
class Tier(models.Model):
    number = models.PositiveSmallIntegerField(default=0)
    description = models.TextField(max_length=800, verbose_name='Description')
    price = models.IntegerField(verbose_name='Price')
    can_message = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tier_user')

    def __str__(self):
        return 'Tier ' + str(self.number)
    
    def save(self, *args, **kwargs):
        amount = Tier.objects.filter(user=self.user).count()
        self.number = amount + 1
        return super().save(*args, **kwargs)

class Subscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriber')
    subscribed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribed')
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, related_name='tier')
    date = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)

    def __str__(self):
        return self.subscriber.username + '==' + self.subscribed.username + '== Tier: ' + str(self.tier.number)
    
    def user_subscribed(sender, instance, *args, **kwargs):
        subscription = instance
        sender = subscription.subscriber
        subscribing = subscription.subscribed

        notify = Notification(sender=sender, user=subscribing, notification_type=3)
        notify.save()

    def user_unsubscribed(sender, instance, *args, **kwargs):
        subscription = instance
        sender = subscription.subscriber
        subscribing = subscription.subscribed

        notify = Notification.objects.filter(sender=sender, user=subscribing, notification_type=3)
        notify.delete()

#Subscription signals stuff:
post_save.connect(Subscription.user_subscribed, sender=Subscription)
post_delete.connect(Subscription.user_unsubscribed, sender=Subscription)