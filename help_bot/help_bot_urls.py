from django.urls import path

from help_bot.views import (MainPage, WebChatBot, web_chat)

urlpatterns = [
    path('', MainPage.as_view(), name='main_page'),
    path('chat_test/', WebChatBot.as_view(), name='web_chat_bot'),
    # re_path(r'^tree/$', tree_page, name='tree'),
    # path('web-chat/', WebChat.as_view(), name='web_chat'),
    path('web-chat/', web_chat, name='web_chat'),
]
