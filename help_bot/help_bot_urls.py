from django.urls import path, re_path

from .views import hello, MainPage, ChatPage, tree_page, ChatTest

urlpatterns = [
    path('', MainPage.as_view(), name='main_page'),
    path('', ChatPage.as_view(), name='chat'),
    path('chat_test/', ChatTest.as_view(), name='chat_test'),
    re_path(r'^tree/$', tree_page, name='tree'),
    path('hello/', hello, name='hello'),
]
