import tweepy

class TwitterCollector:
    def __init__(self, api_key: str):
        self.client = tweepy.Client(api_key)