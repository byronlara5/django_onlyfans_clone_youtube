from django.urls import path
from direct.views import inbox, PeopleWeCanMessage, NewConversation, Directs, SendDirect, LoadMore, UserSearch

urlpatterns = [
    path('', inbox, name='inbox'),
    path('start/', PeopleWeCanMessage, name='people-we-can-message'),
    path('new/<username>', NewConversation, name='new-conversation'),
    path('directs/<username>', Directs, name='directs'),
    path('send/', SendDirect, name='send-direct'),
    path('loadmore/', LoadMore, name='loadmore'),
    path('search/', UserSearch, name='user-search'),

]