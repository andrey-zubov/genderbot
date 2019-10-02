from django.http import HttpResponse
from django.shortcuts import render

from help_bot.models import NeedHelp


def main_page(request):
    return render(request, template_name='help_bot/main_page.html')


def chat_page(request):
    return render(request, template_name='help_bot/chat.html')


def tree_page(request):
    dictionary = {
        'nodes': NeedHelp.objects.all()
    }
    return render(request=request,
                  template_name='help_bot/tree_page.html',
                  context=dictionary)


def hello(request):
    return HttpResponse('Hello Help Bot!', )
