import os
import sys

import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.expanduser(BASE_DIR)
if path not in sys.path:
    sys.path.insert(0, path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HelpBot.settings")
django.setup()

from help_bot.models import NeedHelp


def recreate_need_help_statistic_fk():
    """ обнуление статистики чат бота. """
    nh_all = NeedHelp.objects.all()

    for i in nh_all:
        i_id = i.id
        nh_obj = NeedHelp.objects.get(id=i_id)

        """ сброс ФК """
        nh_obj.statistic_web_id = None
        nh_obj.statistic_telegram_id = None

        """ сохранение объекта дерева, но !!!!
        NeedHelp.save() переопределён - там алгоритм для авто 
        создания и сохранения полей в таблице статистики. 
        Поэто не требуется дополнительных действий. """
        nh_obj.save()


if __name__ == "__main__":
    recreate_need_help_statistic_fk()
