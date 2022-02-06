## 44196397 => Elon Musks's Twitter ID
## Terminal test: python elonbot.py -m "do this now low" -e "git "

import os
import unittest
from unittest.mock import patch

import elonbot
from elonbot import ElonBot


class ElonBotTest(unittest.TestCase):

    # TODO: Optical Character Recognition (OCR)
    # def setUp(self) -> None:
    #     os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'xAIzaSyCvblgUIvkYZU7Aco0bMVrqaQtFy0GZbOY' #'GOOGLE_APPLICATION_CREDENTIALS'

    def test_trigger(self):
        bot = ElonBot("edy_fender", "doge", "delay was lesser then 10", "https://webhook.site/4aee92fd-ae15-4c03-99dc-964f9dc43129", None)
        bot.process_tweet(
            '{"data": {"text": "DOGE backwards is E GOD", "created_at": "2020-07-10T15:00:00.000Z"}, "includes": {"media": [{"url": "..."}]}}')
        bot.process_tweet(
            '{"data": {"text": "Dodge coin is not what we need", "created_at": "2020-07-10T15:00:00.000Z"}, "includes": {"media": [{"url": "..."}]}}')

    def test_get_user_id(self):
        bot = ElonBot("elonmusk", 'doge', "delay was lesser then 10", "https://webhook.site/4aee92fd-ae15-4c03-99dc-964f9dc43129", None)
        bot.get_user_id()

    def test_run(self):
        bot = ElonBot("edy_fender", "doge", "delay was lesser then 10", "https://webhook.site/4aee92fd-ae15-4c03-99dc-964f9dc43129", None)
        bot.run()

