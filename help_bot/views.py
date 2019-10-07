from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from help_bot.models import NeedHelp


class MainPage(TemplateView):
    template_name = 'help_bot/main_page.html'

    def get(self, request, *args, **kwargs):
        return render(request, template_name=self.template_name)

    def post(self, request):
        pass


class ChatPage(TemplateView):
    template_name = 'help_bot/chat.html'

    def get(self, request, *args, **kwargs):
        print("ChatPage - GET\n%s" % request.GET)
        response = {'data': 'some_data.GET',
                    }
        return render(request, template_name=self.template_name, context=response)

    def post(self, request):
        print("ChatPage - POST\n%s" % request.POST)


class ChatTest(TemplateView):
    def get(self, request, *args, **kwargs):
        print('ChatTest.GET\n%s' % request.GET)
        ui = request.GET['us_in']
        q = "%s%s" % (ui, 'test_bot_test_bot')
        return HttpResponse(q)


def tree_page(request):
    dictionary = {
        'nodes': NeedHelp.objects.all()
    }
    return render(request=request,
                  template_name='help_bot/tree_page.html',
                  context=dictionary)


def hello(request):
    return HttpResponse('Hello Help Bot!', )
