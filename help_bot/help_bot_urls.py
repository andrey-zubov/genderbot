from django.urls import path, re_path

from help_bot.views import (MainPage, tree_page, WebChatBot, WebChat)

urlpatterns = [
    path('', MainPage.as_view(), name='main_page'),
    path('chat_test/', WebChatBot.as_view(), name='web_chat_bot'),
    # re_path(r'^tree/$', tree_page, name='tree'),
    path('web-chat/', WebChat.as_view(), name='web_chat'),
]
