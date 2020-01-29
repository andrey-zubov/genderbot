from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import TemplateView

from help_bot.statistic import save_site_statistic
from help_bot.web_chat_logic import chat_req_get


class MainPage(TemplateView):
    template_name = 'help_bot/main_page.html'

    def get(self, request, *args, **kwargs):
        save_site_statistic()
        return render(request, template_name=self.template_name)


class WebChatBot(TemplateView):
    """ Web chat bot pop-up. All Ajax requests come here. """

    def get(self, request, *args, **kwargs):
        save_site_statistic()
        return HttpResponse(chat_req_get(request))


@xframe_options_exempt
def web_chat(request):
    """ iframe window/widget """
    if request.method == "GET":
        save_site_statistic()
        return render(request, template_name='help_bot/chat.html')
