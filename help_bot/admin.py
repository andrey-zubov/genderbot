from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from mptt.admin import MPTTModelAdmin

from help_bot.models import (NeedHelp, TelegramBot, HelpText, StartMessage, StatisticWeb, StatisticTelegram)
from help_bot.statistic import get_chat_statistic


class InlineHelpText(admin.StackedInline):
    model = HelpText
    extra = 1
    max_num = 1


class NeedHelpAdmin(MPTTModelAdmin):
    # TODO:
    #  1) tree admin based on FeinCMS offering drag-drop functionality for moving nodes
    #  http://django-mptt.github.io/django-mptt/admin.html#mptt-admin-draggablempttadmin
    #  2) Admin filter class which filters models related to parent model with all it’s descendants.
    #  http://django-mptt.github.io/django-mptt/admin.html#mptt-admin-treerelatedfieldlistfilter

    inlines = [InlineHelpText]
    model = NeedHelp

    fieldsets = (
        (None, {
            'fields': (('name', 'parent'), 'user_input', 'question', ('go_back', 'go_default', 'is_default', 'link_to'))
        }),
    )
    list_display = ('name', 'parent', 'user_input', 'question', 'go_default', 'link_to', 'go_back', 'is_default')
    search_fields = ('name',)
    autocomplete_fields = ('parent', 'link_to')


class TelegramAdmin(admin.ModelAdmin):
    model = TelegramBot
    fields = ['name', 'token', 'web_hook', 'in_work']
    list_display = ('name', 'token', 'web_hook', 'in_work')
    list_filter = ('web_hook',)
    search_fields = ('name',)


class HelpTextAdmin(admin.ModelAdmin):
    model = HelpText
    fields = ['name', 'text', 'relation_to']
    list_display = ('name', 'relation_to')
    search_fields = ('name',)


class StartMessageAdmin(admin.ModelAdmin):
    model = StartMessage
    fields = ['name', 'text', 'default']
    list_display = ('name', 'text', 'default')
    search_fields = ('name',)


class StatisticWebAdmin(admin.ModelAdmin):
    # model = StatisticWeb
    # readonly_fields = ('count',)
    # fields = ('count',)
    # list_display = ('count',)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            # path('statisticweb/', self.my_view),
            path('', self.admin_site.admin_view(self.my_view)),
        ]
        return my_urls + urls

    def my_view(self, request):
        context = dict(
            # Include common variables for rendering the admin template.
            self.admin_site.each_context(request),
            # Anything else you want in the context...
            my_data=get_chat_statistic(),
        )
        return TemplateResponse(request=request,
                                template="admin/help_bot/statistic_web/my_view/statistic_web_my_view.html",
                                context=context)


class StatisticTelegramAdmin(admin.ModelAdmin):
    model = StatisticTelegram
    readonly_fields = ('count',)
    fields = ('count',)
    list_display = ('count',)


admin.site.register(NeedHelp, NeedHelpAdmin)
admin.site.register(TelegramBot, TelegramAdmin)
admin.site.register(HelpText, HelpTextAdmin)
admin.site.register(StartMessage, StartMessageAdmin)
admin.site.register(StatisticWeb, StatisticWebAdmin)
admin.site.register(StatisticTelegram, StatisticTelegramAdmin)
