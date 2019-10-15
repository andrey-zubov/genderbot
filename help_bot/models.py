from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class NeedHelp(MPTTModel):
    """ TBA
    # http://django-mptt.github.io/django-mptt/models.html
    """
    name = models.CharField(max_length=100, blank=False, verbose_name="Название",
                            help_text="Удобочитаемое имя для родителя.")
    parent = TreeForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                            related_name='children', db_index=True,
                            verbose_name="Родитель", help_text="Кто родитель этого элемента.")

    user_input = models.CharField(max_length=100, default='', blank=False,
                                  verbose_name="Название кнопки",
                                  help_text="Название кнопки, которое отправится в чат.")
    go_back = models.BooleanField(default=False, blank=True, null=True,
                                  verbose_name="Возврат в меню")
    link_to = models.ForeignKey(to='NeedHelp', blank=True, null=True, default=None, on_delete=models.SET_NULL,
                                verbose_name="Ссылка на элемент",
                                help_text="Если эта кнопка является ссылкой на другой элемент дерева -"
                                          " указать этот элемент.")
    question = models.CharField(blank=True, null=True, default='', max_length=100,
                                verbose_name="Вопрос пользователю",
                                help_text="Помощь для администратора при заполнении. "
                                          "Указать, если вопрос есть в тексте бота.")
    """ last element in the tree branch """
    go_default = models.BooleanField(default=False, blank=True, null=True,
                                     verbose_name="Последний элемент?",
                                     help_text="Является ли этот элемент последним для этой ветки дерева.")
    """ hidden root node for a default output that repeats at last tree element """
    is_default = models.BooleanField(default=False, blank=True, null=True,
                                     verbose_name="Элемент по умолчанию",
                                     help_text="Вспомогательная ветка для последних элементов всего дерева.")

    statistic_web = models.ForeignKey(to='StatisticWeb', on_delete=models.CASCADE, null=True, blank=True,
                                      verbose_name="", help_text="")
    statistic_telegram = models.ForeignKey(to='StatisticTelegram', on_delete=models.CASCADE, null=True, blank=True,
                                           verbose_name="", help_text="")

    class MPTTMeta:
        order_insertion_by = ['name']

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        """ AutoCreate and AutoSave ForeignKey(and it values) to StatisticWeb and StatisticTelegram """

        try:
            sw_c = self.statistic_web.count
        except:
            sw_c = 0
        try:
            st_c = self.statistic_telegram.count
        except:
            st_c = 0

        if self.id:
            # sw = NeedHelp.objects.get(id=self.id).statistic_web
            sw = self.statistic_web
            if sw:
                sw.count = sw_c
            else:
                sw = StatisticWeb(id=self.id, count=sw_c)
                sw.count = sw_c
            # st = NeedHelp.objects.get(id=self.id).statistic_telegram
            st = self.statistic_telegram
            if st:
                st.count = st_c
            else:
                st = StatisticTelegram(id=self.id, count=st_c)
                st.count = st_c
        else:
            sw = StatisticWeb(count=sw_c)
            st = StatisticTelegram(count=st_c)

        sw.save()
        self.statistic_web = sw
        st.save()
        self.statistic_telegram = st

        super(NeedHelp, self).save(**kwargs)


class TelegramBot(models.Model):
    """ TBA """
    name = models.CharField(max_length=50, blank=True, null=True)
    token = models.CharField(max_length=100, blank=True, null=True)
    web_hook = models.CharField(max_length=200, blank=True, null=True)
    in_work = models.BooleanField(default=False)  # TODO: rename - default

    def __str__(self):
        return self.name


class HelpText(models.Model):
    """ TBA """
    relation_to = models.OneToOneField(to='NeedHelp', blank=True, null=True,
                                       on_delete=models.SET_NULL)  # TODO: on_delete ???
    name = models.CharField(max_length=100, null=True, blank=True, default='',
                            verbose_name="Назкание текста бота",
                            help_text="Помощь для администратора при заполнении.")
    text = models.TextField(max_length=2000, null=True, blank=True, default='',
                            verbose_name="Текст сообщения",
                            help_text="Текст сообщения бота для отправки в чат.")

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


class StatisticWeb(models.Model):
    """ """
    count = models.PositiveIntegerField(default=0)


class StatisticTelegram(models.Model):
    """ """
    count = models.PositiveIntegerField(default=0)
