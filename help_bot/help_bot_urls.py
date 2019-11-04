from django.urls import path

from help_bot.views import (MainPage, WebChatBot, web_chat)

urlpatterns = [
    path('', MainPage.as_view(), name='main_page'),
    path('chat_test/', WebChatBot.as_view(), name='web_chat_bot'),
    path('web-chat/', web_chat, name='web_chat'),
]
