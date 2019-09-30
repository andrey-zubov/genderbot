from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class NeedHelp(MPTTModel):
    # http://django-mptt.github.io/django-mptt/models.html
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
    name = models.CharField(max_length=50, blank=True, null=True)
    token = models.CharField(max_length=100, blank=True, null=True)
    web_hook = models.CharField(max_length=200, blank=True, null=True)
    in_work = models.BooleanField(default=False)

    def __str__(self):
        return self.name
