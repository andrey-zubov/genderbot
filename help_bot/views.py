from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from help_bot.models import NeedHelp
from help_bot.web_chat_logic import chat_req_get


class MainPage(TemplateView):
    template_name = 'help_bot/main_page.html'

    def get(self, request, *args, **kwargs):
        # print("MainPage.request.META: %s" % request.META)
        return render(request, template_name=self.template_name)

    def post(self, request):
        pass


class ChatPage(TemplateView):
    template_name = 'help_bot/chat_page.html'

    def get(self, request, *args, **kwargs):
        print("ChatPage.GET")
        response = {'data': '-------ChatPage.GET-------', }
        return render(request, template_name=self.template_name, context=response)

    def post(self, request):
        print("ChatPage.POST\n%s" % request.POST)


class ChatTest(TemplateView):

    def get(self, request, *args, **kwargs):
        print('ChatTest.GET: %s' % request.GET)
        return HttpResponse(chat_req_get(request))

    def post(self, request):
        print('ChatTest.POST: %s' % request.POST)


def tree_page(request):
    dictionary = {
        'nodes': NeedHelp.objects.all()
    }
    return render(request=request,
                  template_name='help_bot/tree_page.html',
                  context=dictionary)


def hello(request):
    return HttpResponse('Hello Help Bot!', )
