import concurrent.futures
import logging
import argparse
import textwrap
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
                 crypto_rules: list,
                 message_params: list,
                 use_image_signal: bool,
                 process_tweet_text: Optional[str]):
        self.user = user.lower()
        self.crypto_rules = crypto_rules
        self.message_params = [{"id": count, "message": message[0], "endpoint": message[1],
                                "number_of_requests": message[2]} for count, message in enumerate(message_params)]
        self.use_image_signal = use_image_signal
        self.process_tweet_text = process_tweet_text

        log('Starting elon.py')
        log('  User:', self.user)
        log('  Crypto rules:', self.crypto_rules)
        log('  Message params:\n', json.dumps(self.message_params, indent=4))
        log('  Use image text detection:', self.use_image_signal)
        log('  Process tweet text: ', self.process_tweet_text)



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

    def validate_input(self) -> bool:
        # Validate twitter user
        if self.get_user_id() == '':
            log("Error: Check your twitter user and try again")
            return False

        # Validate message_params inputs
        for message in self.message_params:
            # Validate URL format with regex
            if re.search(r"^https*://", message["endpoint"]) is None:
                log(F"Error: URLs must start with http:// or https://. Please check your message params "
                    F"(ID: {message['id']}) and try again")
                return False

            try:
                # Check if URL exists with requests
                requests.get(message["endpoint"])

                # Validate number_of_requests parameter
                int(message["number_of_requests"])

            except requests.exceptions.ConnectionError:
                log(f"Couldn't find the webhook URL. Please check your message params "
                    f"(ID: {message['id']}) and try again")
                return False

            except ValueError:
                log(F"Error: NUMBER_OF_REQUESTS must be an integer. Please check your message params "
                    F"(ID: {message['id']}) and try again")
                return False

            # Validate if number_of_requests is between the allowed interval
            n = int(message["number_of_requests"])
            if 1 > n or n > 10:
                log(F"Error: NUMBER_OF_REQUESTS MIN is 1 and MAX is 10. Please check your message params "
                    F"(ID: {message['id']})and try again")
                return False

        # If everything goes OK:
        return True

    def webhook(self) -> None:
        # This helper function will be called inside the ThreadPoolExecutor to send the requests in a parallel fashion
        def send_webhook():
            response = requests.post(message["endpoint"], data=message["message"], timeout=10)
            if response.status_code != 200:
                log("Some unexpected error occurred while sending the webhook to (HTTP: {}): {}".format(
                    response.status_code, message["endpoint"]))
                return

            log(f'Webhook sent to {message["endpoint"]} (ID: {message["id"]})')
            return

        # For each message inside the list message_params
        for message in self.message_params:
            # Applying parallelism
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for i in range(int(message["number_of_requests"])):  # This is the number of times the message will be sent
                    executor.submit(send_webhook)

        return None

    def process_tweet(self, tweet: str):
        """ NOTE:
        time.time() returns GMT+0, while status.created_at indicates UTC time. GMT and UTC are basically the same.
        Also, lower is important as python string comparison is case sensitive.
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

                    # Check if the word where re_pattern was found starts with '@'
                    matches = re.findall(rf"(?:^|\s)((?=[\w@]*{re_pattern})[\w@]+)\s", t, flags=re.I)
                    for match in matches:
                        if match[0] != '@':
                            break
                    else:
                        return

                    log(f'Tweet matched pattern {re_pattern}, sending webhook!')

                    self.webhook()
                    return

            log(f'Tweet didn\'t match the pattern {self.crypto_rules}')
        return None

    def run(self) -> None:
        # Check if process_tweet_text is turned on
        if self.process_tweet_text is not None:
            self.process_tweet(self.process_tweet_text)
            return

        # Validate inputs
        if self.validate_input() is False:
            return

        # %(msecs)06d -> this is the micro-seconds adjustment,
        # as time.strptime doesn't have format placeholder for milliseconds
        log_formatter = logging.Formatter("%(asctime)s.%(msecs)06d %(message)s", "%Y-%m-%d %H:%M:%S")

        file_handler = logging.FileHandler(f"log/output-{datetime.now().date()}.log", 'a')
        file_handler.setFormatter(log_formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)

        tweepy.streaming.log.addHandler(file_handler)
        tweepy.streaming.log.addHandler(console_handler)

        # Override on_status method of tweepy class to send the data to ElonBot.process_tweet()
        class Streamer(tweepy.Stream):
            # Defined "bridge" method, so the self keyword relates to the outer class instead of the inner class
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
                                                 'if tweet match criteria', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--user', '-u', help='Twitter user to follow. PLEASE remember not to enter "@"',
                        default="elonmusk")

    parser.add_argument('--message-params', '-m', metavar=("MESSAGE", "ENDPOINT", "NUMBER_OF_REQUESTS"), required=True, action="append", nargs=3,
                        help=textwrap.dedent("ATTENTION: This parameter takes 3 values. The values must be space-separated. "
                                             "First value is the MESSAGE that'll be sent, second value is the webhook ENDPOINT, "
                                             "third value is NUMBER_OF_REQUESTS the bot will send to the Endpoint (MIN is 1 and MAX is 10), "
                                             "Usage:\n"
                                             '--message-params "This is my message" "https://webhook.com" 3'))

    parser.add_argument('--crypto-rules', '-c', default=["doge"], nargs='*',
                        help='Name of the crypto that will be searched on the tweet. ' 
                             'If crypto is found, webhook is sent. '
                             'For multiple rules, please separate them with blank space " "')

    parser.add_argument('--user-image-signal', action="store_true", default=False,
                        help='Extract text from attached twitter images using Google OCR. ' 
                             'ATTENTION: May increase latency')

    parser.add_argument('--process-tweet', default=None,
                        help="Don't subscribe to Twitter feed, only process a single tweet provided as a json string. " 
                             "Useful for test whether the RegEx and crypto rules are working properly")

    args = parser.parse_args()
    bot = ElonBot(args.user,
                  args.crypto_rules,
                  args.message_params,
                  args.user_image_signal,
                  args.process_tweet)

    bot.run()
