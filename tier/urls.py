from django.urls import path
from tier.views import NewTier, FansList, FollowingList, CheckExpiration

urlpatterns = [
    path('newtier/', NewTier, name='newtier'),
    path('myfans/', FansList, name='myfans'),
    path('myfollows/', FollowingList, name='myfollows'),
    path('checkexp/', CheckExpiration, name='check-expiration'),
]