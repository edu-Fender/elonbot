import tweepy
import argparse
import json
import re
import time
import sys

from datetime import datetime
from typing import Optional

import requests
from unidecode import unidecode

from utils import log

ACCESS_TOKEN = '1487797973853614087-h2sxmfF9pTAzIwOABhbNTu2nLJa2TU'
ACCESS_TOKEN_SECRET = 'GLkLvXelvxWj8ftSf63VKcfFzOcHPtf8z8aZwafPVqHD4'
CONSUMER_KEY = 'uYa78RlsHnsT43CX5VEZFmyY3'
CONSUMER_SECRET = 'WvkXSM1d6CSG0z5PpBcmfahjDzpm6mTLnA6BF9HJNZPAM4VmRq'


class ElonBot:
    def __init__(self, user: str,
                 crypto_rules: str,
                 message: str,
                 endpoint: str,
                 process_tweet_text: Optional[str]):
        self.user = user
        self.crypto_rules = crypto_rules
        self.message = message
        self.endpoint = endpoint
        self.process_tweet_text = process_tweet_text

        log('Starting elon.py')
        log('  User:', user)
        log('  Crypto rules:', crypto_rules)
        log('  Message:', message)
        log('  Webhook Endpoint:', endpoint)

    # TODO: Optical Character Recognition (OCR)
    '''
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

    # TODO: Optical Character Recognition (OCR)

    def validate_env(self, verbose=False) -> bool:
        # google_test = not self.use_image_signal or ('GOOGLE_APPLICATION_CREDENTIALS' in os.environ)
        google_test = 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ
        if not google_test and verbose:
            log('Please, provide GOOGLE_APPLICATION_CREDENTIALS environment variable. '
                'Check https://github.com/vslaykovsky/elonbot for details')
        return google_test
    '''

    def get_user_id(self) -> str:

        auth = tweepy.OAuth1UserHandler(
            CONSUMER_KEY, CONSUMER_SECRET,
            ACCESS_TOKEN, ACCESS_TOKEN_SECRET
        )
        api = tweepy.API(auth)

        try:
            user = api.get_user(screen_name=self.user)
            return user.id_str

        except tweepy.errors.NotFound:
            log("Error: Couldn't find user '{}' on twitter".format(self.user))
            sys.exit(-1)

    def webhook(self) -> None:
        response = requests.post(self.endpoint, data=self.message)
        if response.status_code != 200:
            raise Exception("Some unexpected error occurred while sending the webhook(HTTP {}): {}".format(response.status_code, response.text))
        log(f"Webhook sent to {self.endpoint}.")
        return None

    def process_tweet(self, tweet: str):
        tweet = json.loads(tweet)
        if tweet["user"]["screen_name"] == self.user:
            """
            Note: time.time() returns GMT+0 while status.created_at indicates UTC time. GMT and UTC are basically the same
            """
            delay = time.time() - datetime.timestamp(datetime.strptime(tweet["created_at"], '%a %b %d %X %z %Y'))
            log("Tweet received!\n")
            log(json.dumps(tweet, indent=4, sort_keys=True))
            log("DELAY: {}".format(delay))

            tweet_text = tweet["text"]

            # TODO: Optical Character Recognition (OCR)
            '''
            image_url = (tweet_json.get('includes', {}).get('media', [])[0:1] or [{}])[0].get('url', '')
            image_text = ''
            if self.use_image_signal:
               image_text = ElonBot.get_image_text(image_url)
            full_text = f'{tweet_text} {image_text}'
            '''
            if type(self.crypto_rules) != list:
                self.crypto_rules = [self.crypto_rules]

            for re_pattern in self.crypto_rules:
                t = unidecode(tweet_text)
                if re.search(re_pattern, t, flags=re.I) is not None:
                    log(f'Tweet matched pattern "{re_pattern}", sending webhook!')
                    self.webhook()
                    return None

            log(f'Tweet didn\'t match the pattern "{self.crypto_rules[0]}"')
        return None

    def run(self) -> None:
        if self.process_tweet_text is not None:
            self.process_tweet(self.process_tweet_text)
            return

        class Streamer(tweepy.Stream):  # Override on_status method of tweepy class to send the data to ElonBot.process_tweet()
            @staticmethod
            def bridge(obj):
                self.process_tweet(obj)

            def on_data(self, data):
                Streamer.bridge(data)

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
                                                 'depending on tweet content')

    parser.add_argument('--message', '-m', required=True,
                        help='Message that will be sent to the webhook endpoint')

    parser.add_argument('--endpoint', '-e', required=True,
                        help='Webhook Endpoint (URL) to where the messages will be send to')

    parser.add_argument('--user', '-u', help='Twitter user to follow. Please remember not to enter \'@\'. Default: elonmusk)',
                        default="elonmusk")

    parser.add_argument('--crypto-rules', '-c', default="doge",
                        help='\n\nName of the crypto(s) that will be searched on the tweet. '
                             'If crypto is found, webhook is sent. Default: doge')

    parser.add_argument('--process-tweet', default=None,
                        help="Don't subscribe to Twitter feed, only process a single tweet provided as a json string. "
                             "Useful for test whether the RegEx and crypto rules are working properly")

    args = parser.parse_args()
    bot = ElonBot(args.user,
                  args.crypto_rules,
                  args.message,
                  args.endpoint,
                  args.process_tweet)
    bot.run()
