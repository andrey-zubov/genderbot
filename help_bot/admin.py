from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from help_bot.models import (NeedHelp, TelegramBot, HelpText, StartMessage)


# class NeedHelp1t1Admin(admin.StackedInline):
#     model = NeedHelp


class HelpTextForTreeAdmin(admin.StackedInline):
    model = HelpText


class NeedHelpAdmin(MPTTModelAdmin):
    # TODO:
    #  1) tree admin based on FeinCMS offering drag-drop functionality for moving nodes
    #  http://django-mptt.github.io/django-mptt/admin.html#mptt-admin-draggablempttadmin
    #  2) Admin filter class which filters models related to parent model with all it’s descendants.
    #  http://django-mptt.github.io/django-mptt/admin.html#mptt-admin-treerelatedfieldlistfilter

    inlines = [HelpTextForTreeAdmin]

    model = NeedHelp
    fields = ['name', 'parent', 'user_input', 'question', 'go_back', 'link_to', 'go_default',
              'is_default']  # , 'select_help_text'
    list_display = ('name', 'parent', 'user_input', 'question', 'go_back', 'link_to', 'go_default',
                    'is_default',)  #
    # list_filter = ('name', 'parent', 'user_input', 'go_back', 'link_to',)
    search_fields = ('name',)


class TelegramAdmin(admin.ModelAdmin):
    model = TelegramBot
    fields = ['name', 'token', 'web_hook', 'in_work']
    list_display = ('name', 'token', 'web_hook', 'in_work',)
    list_filter = ('name', 'web_hook',)
    search_fields = ('name',)


class HelpTextAdmin(admin.ModelAdmin):
    # inlines = [NeedHelp1t1Admin]
    model = HelpText
    fields = ['name', 'text', 'relation_to']
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)


class StartMessageAdmin(admin.ModelAdmin):
    model = StartMessage
    fields = ['name', 'text', 'default']
    list_display = ('name', 'text', 'default',)
    search_fields = ('name',)


admin.site.register(NeedHelp, NeedHelpAdmin)
admin.site.register(TelegramBot, TelegramAdmin)
admin.site.register(HelpText, HelpTextAdmin)
admin.site.register(StartMessage, StartMessageAdmin)
