import argparse
import json
import os
import re
import time

from datetime import datetime
from typing import Optional

import requests
import tweepy
from unidecode import unidecode

from utils import log


# PLEASE MAKE SURE TO ENTER YOUR RIGHT CREDENTIALS
with open("validation/twitter-credentials.json") as f:
    auth = json.load(f)

ACCESS_TOKEN = auth["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = auth["ACCESS_TOKEN_SECRET"]
CONSUMER_KEY = auth["CONSUMER_KEY"]
CONSUMER_SECRET = auth["CONSUMER_SECRET"]

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'validation/elonbot-340015-23ba720ad52d.json'


class ElonBot:
    def __init__(self, user: str,
                 crypto_rules: str,
                 message: str,
                 endpoints: str,
                 use_image_signal: bool,
                 process_tweet_text: Optional[str]):
        self.user = user.lower()
        self.crypto_rules = [i.replace(' ', '') for i in crypto_rules.split(',')]
        self.message = message
        self.endpoints = [i.replace(' ', '') for i in endpoints.split(',')]
        self.use_image_signal = use_image_signal
        self.process_tweet_text = process_tweet_text

        log('Starting elon.py')
        log('  User:', self.user)
        log('  Crypto rules:', self.crypto_rules)
        log('  Message:', self.message)
        log('  Use image text detection:', self.use_image_signal)
        log('  Webhook endpoints:', self.endpoints)

    @staticmethod
    def get_image_text(uri: str) -> str:
        """Detects text in the file located in Google Cloud Storage or on the Web.
        """
        if uri is None or uri == '':
            return ''
        from google.cloud import vision
        try:
            client = vision.ImageAnnotatorClient()
            image = vision.Image()
            image.source.image_uri = uri
            response = client.text_detection(image=image)
            if response.error.message:
                log('{}\nFor more info on error messages, check: '
                    'https://cloud.google.com/apis/design/errors'.format(response.error.message))
                return ''
            texts = response.text_annotations
            result = ' '.join([text.description for text in texts])
            log('Extracted from the image:', result)
            return result
        except Exception as ex:
            log('Failed to process attached image', ex)
            return ''

    def get_user_id(self) -> str:

        username = self.user

        oauth = tweepy.OAuth1UserHandler(
            CONSUMER_KEY, CONSUMER_SECRET,
            ACCESS_TOKEN, ACCESS_TOKEN_SECRET
        )
        api = tweepy.API(oauth)

        try:
            user = api.get_user(screen_name=username)
            return user.id_str

        except tweepy.errors.NotFound:
            log("Error: Couldn't find user '{}' on twitter".format(username))
            return ''

    def webhook(self) -> None:
        for endpoint in self.endpoints:
            response = requests.post(endpoint, data=self.message)
            if response.status_code != 200:
                log("Some unexpected error occurred while sending the webhook to (HTTP: {}): {}".format(response.status_code, endpoint))
                continue
            log(f"Webhook sent to {endpoint}")
        return None

    def process_tweet(self, tweet: str):
        """ time.time() returns GMT+0 while status.created_at indicates UTC time. GMT and UTC are basically the same.
        Also, lower is important as python string comparison is case sensitive
        """
        tweet = json.loads(tweet)
        if tweet["user"]["screen_name"].lower() == self.user:
            delay = time.time() - datetime.timestamp(datetime.strptime(tweet["created_at"], '%a %b %d %X %z %Y'))
            log("Tweet received!\n")
            log(json.dumps(tweet, indent=4, sort_keys=True))
            log("DELAY: {}".format(delay))

            tweet_text = tweet["text"]

            if self.use_image_signal is True:
                image_url = (tweet.get('entities', {}).get('media', [])[0:1] or [{}])[0].get('media_url', '')
                image_text = ElonBot.get_image_text(image_url)
                tweet_text = f"{tweet_text} {image_text}"

            for re_pattern in self.crypto_rules:
                t = unidecode(tweet_text)
                if re.search(re_pattern, t, flags=re.I) is not None:
                    log(f'Tweet matched pattern "{re_pattern}", sending webhook!')
                    self.webhook()
                    return None

            log(f'Tweet didn\'t match the pattern "{self.crypto_rules}"')
        return None

    def run(self) -> None:
        if self.process_tweet_text is not None:
            self.process_tweet(self.process_tweet_text)
            return
        if self.get_user_id() == '':
            log("Check your params and try again")
            return

        class Streamer(tweepy.Stream):  # Override on_status method of tweepy class to send the data to ElonBot.process_tweet()
            @staticmethod
            def bridge(obj):
                self.process_tweet(obj)

            def on_data(self, data):
                Streamer.bridge(data)

            def on_connection_error(self):
                tweepy.streaming.log.error("Stream connection has errored or timed out. Are the Webhook URL correct?")

        stream = Streamer(
            CONSUMER_KEY, CONSUMER_SECRET,
            ACCESS_TOKEN, ACCESS_TOKEN_SECRET
        )

        while True:
            try:
                log('Subscribing to twitter updates...')
                user_id = self.get_user_id()
                stream.filter(follow=[user_id])
            except Exception as ex:
                log(ex, 'restarting socket...')
                time.sleep(60)
                continue


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Follow Twitter users in real time and send webhook '
                                                 'if tweet match criteria')

    parser.add_argument('--message', '-m', required=True,
                        help='Message that will be sent to the webhook endpoints')

    parser.add_argument('--endpoints', '-e', required=True,
                        help='Webhook endpoints (URL) to where the messages will be send to. PLEASE, separate the values with COMMA ')

    parser.add_argument('--user', '-u', help='Twitter user to follow. PLEASE remember not to enter "@". Default: elonmusk',
                        default="elonmusk")

    parser.add_argument('--crypto-rules', '-c', default="doge",
                        help='\n\nName of the crypto that will be searched on the tweet. '
                             'If crypto is found, webhook is sent. PLEASE, separate the values with COMMA. '
                             'Default: doge')

    parser.add_argument('--user-image-signal', action="store_true", default=False,
                        help='Extract text from attached twitter images using Google OCR. '
                             'ATTENTION: May increase latency')

    parser.add_argument('--process-tweet', default=None,
                        help="Don't subscribe to Twitter feed, only process a single tweet provided as a json string. "
                             "Useful for test whether the RegEx and crypto rules are working properly")

    args = parser.parse_args()
    bot = ElonBot(args.user,
                  args.crypto_rules,
                  args.message,
                  args.endpoints,
                  args.user_image_signal,
                  args.process_tweet)

    bot.run()
