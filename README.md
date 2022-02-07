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
usage: elonbot.py [-h] --message MESSAGE --endpoint ENDPOINT [--user USER] [--crypto-rules CRYPTO_RULES] [--process-tweet PROCESS_TWEET]

optional arguments:
  -h, --help            show this help message and exit
  --message MESSAGE, -m MESSAGE
                        Message that will be sent to the webhook endpoint
  --endpoint ENDPOINT, -e ENDPOINT
                        Webhook Endpoint (URL) to where the messages will be send to
  --user USER, -u USER  Twitter user to follow. Please remember not to enter "@". Default: "elonmusk"
  --crypto-rules CRYPTO_RULES, -c CRYPTO_RULES
                        Name of the crypto that will be searched on the tweet. If crypto is found, webhook is sent. Default: "doge"
  --process-tweet PROCESS_TWEET
                        Don't subscribe to Twitter feed, only process a single tweet provided as a json string. Useful for test whether the RegEx and crypto rules are working properly

```
