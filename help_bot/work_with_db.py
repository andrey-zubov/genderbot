import logging
import os
from time import perf_counter

import django
from telegram import KeyboardButton

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HelpBot.settings")
django.setup()

from help_bot.models import NeedHelp, HelpText, StartMessage


def keyboard_button(massage):
    if massage:
        time_0 = perf_counter()
        print("massage: %s" % massage)

        root_nodes = NeedHelp.objects.root_nodes()
        root_nodes_names = [i.name for i in root_nodes]

        """ [[KeyboardButton(text='Yes')], [KeyboardButton(text='No')]] """
        root_kb = [[KeyboardButton(text=i)] for i in root_nodes_names]

        buttons = root_kb
        text = "Вам нужна помощь?"

        if massage in root_nodes_names:
            parent = root_nodes.get(name=massage)
            children = parent.get_children()
            if children:
                children_names = [i.name for i in children]
                children_kb = [[KeyboardButton(text=i)] for i in children_names]
                buttons = children_kb

                text = HelpText.objects.get(relation_to=parent).text
            else:
                print("No Children in the root: %s" % massage)

        print("TIME keyboard_button() = %s" % (perf_counter() - time_0))
        """
        02.10 20:10 - TIME keyboard_button() = 0.005887855993933044
        """
        return buttons, text
    else:
        print("No massage keyboard_button()")
        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                            level=logging.INFO)
        return None
