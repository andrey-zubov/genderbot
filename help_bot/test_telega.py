import os
import sys

import django
from django.test import TestCase
from telegram import KeyboardButton

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.expanduser(BASE_DIR)
if path not in sys.path:
    sys.path.insert(0, path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HelpBot.settings")
django.setup()

from help_bot.models import (NeedHelp, StartMessage, HelpText)
from help_bot.telega_logic import keyboard_button
from help_bot.utility import time_it


def start_msg() -> (list, str):
    root_nodes = NeedHelp.objects.root_nodes()
    btn_text = [i.user_input for i in root_nodes if not i.is_default]
    btn_to_send = [[KeyboardButton(text=i)] for i in btn_text]
    text_out = StartMessage.objects.get(hello_text=True).text
    return btn_to_send, text_out


def zero_character_input() -> (list, str):
    root_nodes = NeedHelp.objects.root_nodes()
    btn_text = [i.user_input for i in root_nodes if not i.is_default]
    btn_to_send = [[KeyboardButton(text=i)] for i in btn_text]
    text_out = "%s\n\n%s" % (
        StartMessage.objects.get(sorry_text=True).text,
        StartMessage.objects.get(hello_text=True).text
    )
    return btn_to_send, text_out


def btn_input(btn_text: str) -> (list, str):
    tree_element = NeedHelp.objects.get(user_input=btn_text, link_to=None)
    child_element = tree_element.get_children()
    btn_text = [i.user_input for i in child_element]
    btn_out = [[KeyboardButton(text=i)] for i in btn_text]

    text_out = HelpText.objects.get(relation_to=tree_element.id).text

    return btn_out, text_out


class TelegramTests(TestCase):
    """ python manage.py test help_bot/ --keepdb """

    @time_it
    def test_start_input(self):
        """ out == (btn_to_send, text_out) """
        self.assertEqual(keyboard_button("/start", 123456), start_msg())

    @time_it
    def test_zero_input(self):
        self.assertEqual(keyboard_button("", 123456), zero_character_input())

    @time_it
    def test_one_character_input(self):
        self.assertEqual(keyboard_button("1", 123456), zero_character_input())

    @time_it
    def test_text_input(self):
        btn_name = 'Юридическая помощь'
        self.assertEqual(keyboard_button(btn_name, 123456), btn_input(btn_name))

    @time_it
    def test_tree_root_nodes(self):
        # self.maxDiff = None
        root_nodes = NeedHelp.objects.root_nodes()
        btn_text = [i.user_input for i in root_nodes if not i.is_default]
        # print(btn_text)
        for i, btn_name in enumerate(btn_text, 1):
            self.assertEqual(keyboard_button(btn_name, i), btn_input(btn_name))


if __name__ == "__main__":
    TelegramTests()
