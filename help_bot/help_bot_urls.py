from django.urls import path, re_path

from .views import hello, main_page, chat_page, tree_page

urlpatterns = [
    path('', main_page, name='main_page'),
    path('chat/', chat_page, name='chat'),
    re_path(r'^tree/$', tree_page, name='tree'),
    path('hello/', hello, name='hello'),
]
