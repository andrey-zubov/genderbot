from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class NeedHelp(MPTTModel):
    """ TBA
    # http://django-mptt.github.io/django-mptt/models.html
    """

    name = models.CharField(max_length=100)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                            related_name='children', db_index=True)  # TODO: on_delete ?

    user_input = models.CharField(max_length=100, default='-')
    go_back = models.BooleanField(default=False, blank=True, null=True)
    link_to = models.ForeignKey(to='NeedHelp', blank=True, null=True, default=None,
                                on_delete=models.CASCADE)  # TODO: on_delete ?

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
    relation_to = models.OneToOneField(to='NeedHelp', on_delete=models.CASCADE)  # TODO: on_delete ???

    name = models.CharField(max_length=100, default='-')
    text = models.TextField(max_length=2000, default='-')

    def __str__(self):
        return self.name


class StartMessage(models.Model):
    """ TBA """
    name = models.CharField(default='-', max_length=100)
    text = models.TextField(max_length=1000, default='-')

    def __str__(self):
        return self.name


class ChatPosition(models.Model):
    """ TBA """
    chat_id = models.PositiveIntegerField(default=0)
    user_chat_position = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.chat_id
