from django.test import TestCase

from help_bot.telega_logic import keyboard_button
from help_bot.utility import time_it


class TelegramTests(TestCase):

    @time_it
    def test_html_tags(self):
        """ out == (btn_to_send, text_out) """
        self.assertEqual(keyboard_button("/start", 123456), ([], ''))
        self.assertEqual(keyboard_button("", 123456), ([], '\n\n'))
        self.assertEqual(keyboard_button("1", 123456), ([], '\n\n'))
        self.assertEqual(keyboard_button("Приют", 123456), ([], '\n\n'))


if __name__ == "__main__":
    TelegramTests()
