import os
import unittest
from unittest.mock import patch

import elonbot
from elonbot import ElonBot


class ElonBotTest(unittest.TestCase):

    def setUp(self) -> None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google app credentials'
        os.environ['TWITTER_BEARER_TOKEN'] = 'TWITTER_BEARER_TOKEN'

    @patch.object(elonbot.ElonBot, 'get_image_text', lambda url: '')
    def test_trigger(self):
        bot = ElonBot('elonmusk', {'doge': 'DOGE', 'btc|bitcoin': 'BTC'}, True, process_tweet_text=None)
        bot.process_tweet(
            '{"data": {"text": "DOGE backwards is E GOD"}, "includes": {"media": [{"url": "..."}]}}')
        bot.process_tweet(
            '{"data": {"text": "Dodge coin is not what we need"}, "includes": {"media": [{"url": "..."}]}}')

    @patch.object(elonbot.ElonBot, 'get_image_text', lambda url: '')
    def test_isolated(self):
        bot = ElonBot('elonmusk', {'doge': 'DOGE', 'btc|bitcoin': 'BTC'}, True, process_tweet_text=None)
        bot.process_tweet(
            '{"data": {"text": "DOGE backwards is E GOD"}, "includes": {"media": [{"url": "..."}]}}')
        bot.process_tweet(
            '{"data": {"text": "Dodge coin is not what we need"}, "includes": {"media": [{"url": "..."}]}}')
