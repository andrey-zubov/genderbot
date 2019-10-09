from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class NeedHelp(MPTTModel):
    """ TBA
    # http://django-mptt.github.io/django-mptt/models.html
    """
    name = models.CharField(max_length=100)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                            related_name='children', db_index=True)  # TODO: on_delete ?
    user_input = models.CharField(max_length=100, default='')
    go_back = models.BooleanField(default=False, blank=True, null=True)
    link_to = models.ForeignKey(to='NeedHelp', blank=True, null=True, default=None,
                                on_delete=models.CASCADE)  # TODO: on_delete ?
    select_help_text = models.ForeignKey(to='HelpText', blank=True, null=True,
                                         on_delete=models.SET_NULL)
    question = models.CharField(blank=True, null=True, default='', max_length=100)
    """ last element in the tree branch """
    go_default = models.BooleanField(default=False, blank=True, null=True)
    """ hidden root node for a default output that repeats at last tree element """
    is_default = models.BooleanField(default=False, blank=True, null=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class TelegramBot(models.Model):
    """ TBA """
    name = models.CharField(max_length=50, blank=True, null=True)
    token = models.CharField(max_length=100, blank=True, null=True)
    web_hook = models.CharField(max_length=200, blank=True, null=True)
    in_work = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class HelpText(models.Model):
    """ TBA """
    relation_to = models.OneToOneField(to='NeedHelp', blank=True, null=True,
                                       on_delete=models.SET_NULL)  # TODO: on_delete ???
    name = models.CharField(max_length=100, null=True, blank=True, default='')
    text = models.TextField(max_length=2000, null=True, blank=True, default='')

    def __str__(self):
        return self.name


class StartMessage(models.Model):
    """ TBA """
    name = models.CharField(default='', max_length=100)
    text = models.TextField(max_length=1000, default='')
    default = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.name


class ChatPositionTelegram(models.Model):
    """ Key element of my algorithm - remember a user position to send relevant questions to user.
    position == MPTT (NeedHelp) element id """
    """ telegram chat id """
    chat_id = models.PositiveIntegerField(default=0)
    """ user chat-bot position """
    position = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.chat_id


class ChatPositionWeb(models.Model):
    """ Key element of my algorithm - remember user position to send relevant questions to user.
    position == MPTT (NeedHelp) element id """
    """ user IP address """
    ip_address = models.GenericIPAddressField()
    """ user chat-bot position """
    position = models.PositiveIntegerField(default=0)
