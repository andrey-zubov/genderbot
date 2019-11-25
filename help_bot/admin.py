from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from mptt.admin import MPTTModelAdmin

from help_bot.models import (NeedHelp, TelegramBot, HelpText, StartMessage, StatisticTelegram,
                             StatisticAttendance, ChatBotIframe, EditionButtons)
from help_bot.statistic import get_chat_statistic


class InlineHelpText(admin.StackedInline):
    model = HelpText
    extra = 1
    fields = ('name', ('text', 'geo_link_name', 'address', 'latitude', 'longitude'), 'telegram_geo_url')


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
    fields = ('name', 'in_work', 'token')  # 'web_hook'
    list_display = ('name', 'token', 'in_work')  # , 'web_hook'
    list_filter = ('in_work',)
    search_fields = ('name',)


class HelpTextAdmin(admin.ModelAdmin):
    model = HelpText
    fields = ('name', ('text', 'address', 'latitude', 'longitude'), 'relation_to', 'telegram_geo_url')
    list_display = ('name', 'relation_to', 'address', 'latitude', 'longitude')
    search_fields = ('name', 'address')


class StartMessageAdmin(admin.ModelAdmin):
    model = StartMessage
    fields = ('name', 'text', 'hello_text', "sorry_text")
    list_display = ('name', 'text', 'hello_text', "sorry_text")
    search_fields = ('name',)


class StatisticAdmin(admin.ModelAdmin):
    """ Custom admin view! """
    custom_template = "admin/help_bot/statistic_web/my_view/statistic_web_my_view.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path('', self.admin_site.admin_view(self.custom_view)),
                   ]
        return my_urls + urls

    def custom_view(self, request):
        context = dict(
            # Include common variables for rendering the admin template.
            self.admin_site.each_context(request),
            # Anything else you want in the context...
            my_data=get_chat_statistic(),
        )
        return TemplateResponse(request=request, template=self.custom_template, context=context)


class StatisticTelegramAdmin(admin.ModelAdmin):
    model = StatisticTelegram
    readonly_fields = ('count',)
    fields = ('count',)
    list_display = ('count',)


admin.site.register(NeedHelp, NeedHelpAdmin)
admin.site.register(TelegramBot, TelegramAdmin)
admin.site.register(HelpText, HelpTextAdmin)
admin.site.register(StartMessage, StartMessageAdmin)
admin.site.register(StatisticAttendance, StatisticAdmin)


class ChatBotIframeAdmin(admin.ModelAdmin):
    pass


class EditionButtonsAdmin(admin.ModelAdmin):
    model = EditionButtons
    fields = ('btn_name', 'btn_active', 'btn_position_start')  # 'btn_position_end'
    list_display = ('btn_name', 'btn_active', 'btn_position_start')


admin.site.register(ChatBotIframe, ChatBotIframeAdmin)
admin.site.register(EditionButtons, EditionButtonsAdmin)
