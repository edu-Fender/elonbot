# 1487797973853614087 => My Twitter ID
# 44196397 => Elon Musk's Twitter ID
# https://webhook.site/4aee92fd-ae15-4c03-99dc-964f9dc43129?,
# https://web.hook.sh/bc88e3d7-96f1-4f65-8a5a-201012e4b3fd => My Webhook !

import unittest
from unittest.mock import patch

import elonbot
from elonbot import ElonBot


class ElonBotTest(unittest.TestCase):

    def test_trigger(self):
        bot = ElonBot("edy_fender", "doge", "delay was lesser then 10", "https://webhook.site/4aee92fd-ae15-4c03-99dc-964f9dc43129", None)
        bot.process_tweet(
            '{"data": {"text": "DOGE backwards is E GOD", "created_at": "2020-07-10T15:00:00.000Z"}, "includes": {"media": [{"url": "..."}]}}')
        bot.process_tweet(
            '{"data": {"text": "Dodge coin is not what we need", "created_at": "2020-07-10T15:00:00.000Z"}, "includes": {"media": [{"url": "..."}]}}')

    #@patch.object(elonbot.ElonBot, 'get_image_text', lambda url: '')
    def test_ocr(self):
        bot = ElonBot("edy_fender", 'doge', "delay was lesser then 10", "https://webhook.site/4aee92fd-ae15-4c03-99dc-964f9dc43129", False, None)
        a = bot.get_image_text("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSlmMGS_wWmQVKBEeG0u3sfFsNeJ0a4S5CT5A&usqp=CAU")

    def test_get_user_id(self):
        bot = ElonBot("edy_fenderxdxd", 'doge', "delay was lesser then 10", "https://webhook.site/4aee92fd-ae15-4c03-99dc-964f9dc43129", False, None)
        user_id = bot.get_user_id()
        print(user_id)

    def test_webhook(self):
        bot = ElonBot("edy_fender", ["doge", "btc", "etherium"],
                      [["oioi", "https://whook.site/4aee92fd-ae15-4c03-99dc-964f9dc43129?", 4]], True, None)
        bot.webhook()

    def test_run(self):
        bot = ElonBot("edy_fender", ["doge", "btc", "etherium"], [["oioi", "https://wehook.site/4aee92fd-ae15-4c03-99dc-964f9dc43129?", 4]], True, None)
        bot.run()

