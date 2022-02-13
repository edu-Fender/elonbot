# Elonbot

Bot that uses Elon Musk`s tweets to send message to Webhook Endpoints if tweet matches criteria. 
Here is how it works:

1. Subscribes to someone's ([elonmusk](http://twitter.com/elonmusk)?) tweets 
2. Automatically detects mentions of DOGE or other crypto in the image(or text) 
![Elon's tweet](elontweet.png)
3. Send message to the Webhook Endpoint `--endpoint`


## Installation

```shell
git clone http://github.com/edu-fender/elonbot
pip install requests tweepy google-cloud-vision unidecode
```

## Running

1. Set the Twitter API 1.1v credentials at the beginning of elonbot.py
    * You will notice the Twitter Oauth variables are assigned to a json file that is not part of this repository 
      (for obvious reasons)
    * Just change the value of these variables with your own credentials if you don't want to store them in a file
1. [Optional] Add image text recognition support with Google OCR
    * Use the [following documentation](https://cloud.google.com/vision/docs/setup) to access Google Vision API
    * Export path to your google vision configuration. 
      * Linux `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/google_vision_credentials.json"`
      * Windows `set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\google_vision_credentials.json"`
2. Run elonbot.py

Here are some examples of how to run Elonbot. All examples are provided for Linux. 
For Windows make sure you use [correct escaping](https://ss64.com/nt/syntax-esc.html) 

With image text recognition:

```shell
python elonbot.py --message="this is a webhook" --endpoint="https://webhook.site/some-webhoook-endpoint" --use-image-signal
```

No image text recognition
```shell
python elonbot.py --message="this is a webhook" --endpoint="https://webhook.site/some-webhoook-endpoint"
```

Changing default values '--user' and '--crypto--rules'
```shell
python elonbot.py --user="jeffbezos" --crypto-rules="btc" --message="this is a webhook" --endpoint="https://webhook.site/some-webhoook-endpoint"
```


Get help:
```shell
(base) C:\Users\anewe\PycharmProjects\elonbot>python elonbot.py --help
usage: elonbot.py [-h] --message MESSAGE --endpoints ENDPOINTS [--user USER] [--crypto-rules CRYPTO_RULES] [--user-image-signal] [--process-tweet TWEET_TO_PROCESS]

optional arguments:
  -h, --help            show this help message and exit
  --message MESSAGE, -m MESSAGE
                        Message that will be sent to the webhook endpoints
  --endpoints ENDPOINTS, -e ENDPOINTS
                        Webhook endpoints (URL) to where the messages will be sent. PLEASE, separate the values with COMMA
  --user USER, -u USER  Twitter user to follow. PLEASE remember not to enter "@". Default: elonmusk
  --crypto-rules CRYPTO_RULES, -c CRYPTO_RULES
                        Name of the crypto that will be searched on the tweet. If crypto is found, webhook is sent. PLEASE, separate the values with COMMA. Default: doge
  --user-image-signal   Extract text from attached twitter images using Google OCR. ATTENTION: May increase latency
  --process-tweet TWEET_TO_PROCESS
                        Don't subscribe to Twitter feed, only process a single tweet provided as a json string. Useful for test whether the RegEx and crypto rules are working properly

```
