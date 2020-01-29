import logging

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class NeedHelp(MPTTModel):
    """ Main chat-bot Model. """
    """ MPTT: http://django-mptt.github.io/django-mptt/models.html """
    name = models.CharField(max_length=100, blank=False, verbose_name="Название",
                            help_text="Удобочитаемое имя для родителя.")
    parent = TreeForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                            related_name='children', db_index=True,
                            verbose_name="Родитель", help_text="Кто родитель этого элемента.")
    """ Normal model fields. """
    user_input = models.CharField(max_length=100, default='', blank=False,
                                  verbose_name="Название кнопки",
                                  help_text="Название кнопки, которое отправится в чат.")
    go_back = models.BooleanField(default=False, blank=True, null=True,
                                  verbose_name="Возврат в меню",
                                  help_text="«ДА» - вернуть пользователя к стартовым вопросам.")
    link_to = models.ForeignKey(to='NeedHelp', blank=True, null=True, default=None, on_delete=models.SET_NULL,
                                verbose_name="Ссылка на элемент",
                                help_text="Если эта кнопка является ссылкой на другой элемент дерева -"
                                          " указать этот элемент.")
    question = models.CharField(blank=True, null=True, default='', max_length=100,
                                verbose_name="Вопрос пользователю",
                                help_text="Помощь для администратора при заполнении.<br>"
                                          "Указать, если вопрос есть в тексте бота.")
    """ last element in the tree branch """
    go_default = models.BooleanField(default=False, blank=True, null=True,
                                     verbose_name="Последний элемент ветки?",
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

    class Meta:
        verbose_name = 'Дерево диалога'
        verbose_name_plural = 'Дерево диалога'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        """ AutoCreate and AutoSave ForeignKey(and it values) to StatisticWeb and StatisticTelegram """

        try:
            sw_c = self.statistic_web.count
        except Exception as ex:
            logging.error("Exception in NeedHelp.save().statistic_web\n%s" % ex)
            sw_c = 0
        try:
            st_c = self.statistic_telegram.count
        except Exception as ex:
            logging.error("Exception in NeedHelp.save().statistic_telegram\n%s" % ex)
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
    """ Set up Telegram properties. """
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Название")
    token = models.CharField(max_length=100, blank=True, null=True)
    web_hook = models.CharField(max_length=200, blank=True, null=True)
    in_work = models.BooleanField(default=False,
                                  verbose_name="Является основным",
                                  help_text="Только ОДИН telegram bot может быть выбран как основной для работы.")

    class Meta:
        verbose_name = 'Телеграм бот'
        verbose_name_plural = 'Телеграм боты'

    def __str__(self):
        return self.name


class HelpText(models.Model):
    """ Bot answer text. """
    relation_to = models.ForeignKey(to='NeedHelp', blank=True, null=True,
                                    on_delete=models.SET_NULL, verbose_name="Относится к элементу дерева")
    name = models.CharField(max_length=100, null=True, blank=True, default='',
                            verbose_name="Назкание текста бота",
                            help_text="Помощь для администратора при заполнении.")
    text = models.TextField(max_length=2000, null=True, blank=True, default='',
                            verbose_name="Текст сообщения",
                            help_text="Текст сообщения бота для отправки в чат.<br>"
                                      "Пример номера телефона: 8 (017) 123-45-67 или +375 (12) 123-45-67")

    # geo_link
    geo_link_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Имя для гео-ссылки",
                                     help_text="пример: ТЦСОН (необходимо только краткое сокращение).<br>"
                                               "Обязательно для создания гео-ссылки в web-чате - увеличивает точность!")
    address = models.CharField(max_length=100, null=True, blank=True,
                               verbose_name="Адрес",
                               help_text="пример: г. Лида, ул. Варшавская, 9.<br>"
                                         "Обязательно для создания гео-ссылки в web-чате!")

    latitude = models.FloatField(blank=True, null=True, verbose_name="Широта",
                                 help_text="Широты РБ от 51.258872 до 56.171949.<br>"
                                           "Обязательно для создания гео-ссылки в web-чате - увеличивает точность!")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Долгота",
                                  help_text="Долгота РБ от 23.176563 до 32.779784.<br>"
                                            "Обязательно для создания гео-ссылки в web-чате - увеличивает точность!")

    telegram_geo_url = models.URLField(max_length=500, blank=True, null=True,
                                       verbose_name="Ссылка на объект на карте",
                                       help_text="<b>Только для Телеграма!!! Максимум 500 символов.</b><br>"
                                                 "Обязательно для создания гео-ссылки в Телеграм-чате!")

    class Meta:
        verbose_name = 'Текст сообщения бота'
        verbose_name_plural = 'Тексты сообщений бота'

    def __str__(self):
        return self.name


class StartMessage(models.Model):
    """ Hello message. """
    name = models.CharField(default='', max_length=100, verbose_name="Название текста")
    text = models.TextField(max_length=1000, default='', verbose_name="Текст сообщения")
    hello_text = models.BooleanField(default=False, blank=True, null=True,
                                     verbose_name="Текст приветствия по умолчанию",
                                     help_text="Только одно сообщение-приветствие может быть активным,<br>"
                                               "т.к. отправляется пользователю при старте чата.")
    sorry_text = models.BooleanField(default=False, blank=True, null=True,
                                     verbose_name="Текст об ошибке",
                                     help_text="Только одно сообщение-ошибка может быть активным,<br>"
                                               "т.к. отправляется пользователю при неправильном вводе.")

    class Meta:
        verbose_name = 'Стартовое сообщение бота'
        verbose_name_plural = 'Стартовое сообщение бота'

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
    """ NeedHelp Tree buttons clicks for web chat. """
    count = models.PositiveIntegerField(default=0, verbose_name="Колличество")


class StatisticTelegram(models.Model):
    """ NeedHelp Tree buttons clicks for Telegram chat. """
    count = models.PositiveIntegerField(default=0, verbose_name="Колличество")


class StatisticAttendance(models.Model):
    """ days, months, year. """
    date_point = models.DateField(auto_now=True)
    web_chat_count = models.PositiveIntegerField(default=0)
    telegram_chat_count = models.PositiveIntegerField(default=0)
    site_open = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Статистика чат-бота'
        verbose_name_plural = 'Статистика чат-бота'


class ChatBotIframe(models.Model):
    """ How to insert web chat bot code to your page. """
    iframe_code_name = models.CharField(default='', blank=True, null=True, max_length=50)
    iframe_code = models.TextField(default='', blank=True, null=True, max_length=5000)

    def __str__(self):
        return self.iframe_code_name

    class Meta:
        verbose_name = 'Код для вставки на сайт'
        verbose_name_plural = 'Код для вставки на сайт'


class EditionButtons(models.Model):
    """ buttons exp: "Go back"
    """
    btn_name = models.CharField(default='', blank=True, null=True, max_length=50,
                                verbose_name="Название кнопки",
                                help_text="")
    btn_active = models.BooleanField(default=False, blank=True, null=True,
                                     verbose_name="Кнопка активна",
                                     help_text="")
    btn_position_start = models.BooleanField(default=False, blank=True, null=True,
                                             verbose_name="В начале списка кнопок чата",
                                             help_text="да/нет")
    btn_position_end = models.BooleanField(default=False, blank=True, null=True,
                                           verbose_name="В конце списка кнопок чата",
                                           help_text="да/нет")

    def __str__(self):
        return self.btn_name

    class Meta:
        verbose_name = 'Дополнительная кнопка чата'
        verbose_name_plural = 'Дополнительные кнопки чата'
