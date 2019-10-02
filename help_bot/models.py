from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class NeedHelp(MPTTModel):
    """ TBA
    # http://django-mptt.github.io/django-mptt/models.html
    """

    name = models.CharField(max_length=20, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                            related_name='children', db_index=True)

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

    relation_to = models.OneToOneField(to='NeedHelp', on_delete=models.CASCADE)
    # +smt like slag
    text = models.TextField(blank=True, null=True, max_length=2000)


class StartMessage(models.Model):
    """ TBA """
    text = models.TextField(blank=True, null=True, max_length=1000)
