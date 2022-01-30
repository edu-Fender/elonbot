import argparse
import json
import os
import re
import sys
import time
from typing import Dict, Optional

import requests
from unidecode import unidecode

from twitter_utils import create_headers, reset_twitter_subscription_rules
from utils import log

class ElonBot:
    def __init__(self, user: str,
                 crypto_rules: Dict[str, str],
                 use_image_signal: bool,
                 process_tweet_text: Optional[str]):
        self.user = user
        self.crypto_rules = crypto_rules
        self.use_image_signal = use_image_signal
        self.process_tweet_text = process_tweet_text
        if not self.validate_env():
            return
        log('Starting elon.py')
        log('  User:', user)
        log('  Crypto rules:', crypto_rules)
        log('  Use image signal:', use_image_signal)

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

    def validate_env(self, verbose=False) -> bool:
        google_test = not self.use_image_signal or ('GOOGLE_APPLICATION_CREDENTIALS' in os.environ)
        if not google_test and verbose:
            log('Please, provide GOOGLE_APPLICATION_CREDENTIALS environment variable. '
                'Check https://github.com/vslaykovsky/elonbot for details')
        twitter_test = 'TWITTER_BEARER_TOKEN' in os.environ
        if not twitter_test and verbose:
            log('Please, provide TWITTER_BEARER_TOKEN environment variable. '
                'Check https://github.com/vslaykovsky/elonbot for details')
        return google_test and twitter_test

    def process_tweet(self, tweet_json: str):
        tweet_json = json.loads(tweet_json)
        log("Tweet received\n", json.dumps(tweet_json, indent=4, sort_keys=True), "\n")
        tweet_text = tweet_json['data']['text']
        image_url = (tweet_json.get('includes', {}).get('media', [])[0:1] or [{}])[0].get('url', '')
        image_text = ''
        if self.use_image_signal:
            image_text = ElonBot.get_image_text(image_url)
        full_text = f'{tweet_text} {image_text}'
        for re_pattern, ticker in self.crypto_rules.items():
            t = unidecode(full_text)
            if re.search(re_pattern, t, flags=re.I) is not None:
                log(f'Tweet matched pattern "{re_pattern}", buying corresponding ticker {ticker}')
                ####return self.trade(ticker)
        return None

    def run(self, timeout: int = 24 * 3600) -> None:
        if self.process_tweet_text is not None:
            self.process_tweet(self.process_tweet_text)
            return
        reset_twitter_subscription_rules(self.user)
        while True:
            try:
                params = {'expansions': 'attachments.media_keys',
                          'media.fields': 'preview_image_url,media_key,url',
                          'tweet.fields': 'attachments,entities'}
                response = requests.get(
                    "https://api.twitter.com/2/tweets/search/stream",
                    headers=create_headers(), params=params, stream=True, timeout=timeout
                )
                log('Subscribing to twitter updates. HTTP status:', response.status_code)
                if response.status_code != 200:
                    raise Exception("Cannot get stream (HTTP {}): {}".format(response.status_code, response.text))
                for response_line in response.iter_lines():
                    if response_line:
                        self.process_tweet(response_line)
            except Exception as ex:
                log(ex, 'restarting socket')
                time.sleep(60)
                continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Trade cryptocurrency at Binance using Twitter signal')
    parser.add_argument('--user', help='Twitter user to follow. Example: elonmusk (please, remember not to put \'@\')',
                        required=True)
    parser.add_argument('--crypto-rules', help='\n\nJSON dictionary, where keys are regular expression patterns, '
                                               'values are corresponding cryptocurrency tickers. elonbot.py '
                                               'uses regular expressions to find tweets that mention cryptocurrency,'
                                               'then buys corresponding crypto ticker',
                        default=json.dumps({'doge': 'DOGE', 'btc|bitcoin': 'BTC'}))
    parser.add_argument('--use-image-signal', action='store_true',
                        help='Extract text from attached twitter images using Google OCR. '
                             'Requires correct value of GOOGLE_APPLICATION_CREDENTIALS environment variable.'
                             'Check https://github.com/vslaykovsky/elonbot for more details',
                        default=False)
    parser.add_argument('--process-tweet',
                        help="Don't subscribe to Twitter feed, only process a single tweet provided as a json string "
                             "(useful for testing). Example value: "
                             "'{\"data\": {\"text\": \"Dodge coin is not what we need\"}, \"includes\": {\"media\": "
                             "[{\"url\": \"...\"}]}}'",
                        default=None)
    args = parser.parse_args()
    bot = ElonBot(args.user,
                  json.loads(args.crypto_rules),
                  args.use_image_signal,
                  args.process_tweet)
    if not bot.validate_env(verbose=True):
        sys.exit(-1)
    bot.run()
