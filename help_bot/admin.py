from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import NeedHelp, TelegramBot


class NeedHelpAdmin(MPTTModelAdmin):
    # TODO:
    #  1) tree admin based on FeinCMS offering drag-drop functionality for moving nodes
    #  http://django-mptt.github.io/django-mptt/admin.html#mptt-admin-draggablempttadmin
    #  2) Admin filter class which filters models related to parent model with all it’s descendants.
    #  http://django-mptt.github.io/django-mptt/admin.html#mptt-admin-treerelatedfieldlistfilter

    model = NeedHelp
    fields = ['name', 'parent']
    list_display = ('name', 'parent',)
    list_filter = ('name', 'parent',)
    search_fields = ('name',)


class TelegramAdmin(admin.ModelAdmin):
    model = TelegramBot
    fields = ['name', 'token', 'web_hook', 'in_work']
    list_display = ('name', 'token', 'web_hook', 'in_work',)
    list_filter = ('name', 'web_hook',)
    search_fields = ('name',)


admin.site.register(NeedHelp, NeedHelpAdmin)
admin.site.register(TelegramBot, TelegramAdmin)
