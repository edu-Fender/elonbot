# 1487797973853614087 => My Twitter ID
# 44196397 => Elon Musk's Twitter ID
# https://webhook.site/4aee92fd-ae15-4c03-99dc-964f9dc43129? => My Webhook !

import os
import unittest
from unittest.mock import patch

import elonbot
from elonbot import ElonBot


class ElonBotTest(unittest.TestCase):

    #TODO: Optical Character Recognition (OCR)
    def setUp(self) -> None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'xAIzaSyCvblgUIvkYZU7Aco0bMVrqaQtFy0GZbOY' #'GOOGLE_APPLICATION_CREDENTIALS'

    def test_trigger(self):
        bot = ElonBot("edy_fender", "doge", "delay was lesser then 10", "https://webhook.site/4aee92fd-ae15-4c03-99dc-964f9dc43129", None)
        bot.process_tweet(
            '{"data": {"text": "DOGE backwards is E GOD", "created_at": "2020-07-10T15:00:00.000Z"}, "includes": {"media": [{"url": "..."}]}}')
        bot.process_tweet(
            '{"data": {"text": "Dodge coin is not what we need", "created_at": "2020-07-10T15:00:00.000Z"}, "includes": {"media": [{"url": "..."}]}}')

    #@patch.object(elonbot.ElonBot, 'get_image_text', lambda url: '')
    def test_ocr(self):
        a = ElonBot.get_image_text('https://academy.bit2me.com/wp-content/uploads/2021/07/Dogecoin-bit2meacademy.png')
        print(a)

    def test_get_user_id(self):
        bot = ElonBot("edy_fender", 'doge', "delay was lesser then 10", "https://webhook.site/4aee92fd-ae15-4c03-99dc-964f9dc43129", None)
        user_id = bot.get_user_id()
        print(user_id)

    def test_run(self):
        bot = ElonBot("edy_fender", "doge", """Mainacc(BTCUSD) {
Cancel(which=all);
Market(position=0);
managed(side=sell, amount=100, entry=market, stoploss=200, takeprofit=175);
}
#bot""", "https://webhook.site/4aee92fd-ae15-4c03-99dc-964f9dc43129?", None)
        bot.run()

