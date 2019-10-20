from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from help_bot.models import NeedHelp
from help_bot.statistic import save_site_statistic
from help_bot.web_chat_logic import chat_req_get


class MainPage(TemplateView):
    template_name = 'help_bot/main_page.html'

    def get(self, request, *args, **kwargs):
        save_site_statistic()
        return render(request, template_name=self.template_name)

    def post(self, request):
        pass


class WebChatBot(TemplateView):
    """ Web chat bot pop-up. All Ajax requests come here. """

    def get(self, request, *args, **kwargs):
        return HttpResponse(chat_req_get(request))

    def post(self, request):
        pass


def tree_page(request):
    dictionary = {
        'nodes': NeedHelp.objects.all()
    }
    return render(request=request, template_name='help_bot/tree_page.html', context=dictionary)
