"""
Collection Notes
- Very limited # of posts that can be collected

- Keep track of which tweet IDs have already been collected
"""

import tweepy
import json 
import time 

import fields 
from .base_collector import TwitterCollector



class IDTwitterCollector(TwitterCollector):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def get_tweets_by_ids(self, tweet_ids: list):
        """
        Given a list of any number of tweet ids, break them into 100 tweet chunks and get the data for each tweet
        assembling all the data together into a single list of dictionaries

        We can only send 15 requests per 15 minutes
        """
        start_time = time.time()
        requests_made = 0
        for i in range(0, len(tweet_ids), 100):
            # Check if we can make a request i.e. if our requests per minutes is less than 1 
            elapsed_minutes = (time.time() - start_time) / 60
            if requests_made > elapsed_minutes:
                print(f"Sleeping for 1 minute. Requests made: {requests_made}, Elapsed minutes: {elapsed_minutes}")
                time.sleep(60)

            try:
                yield self._format_tweet_results(self._get_multiple_tweets_by_ids(tweet_ids[i:i + 100]))
            except tweepy.errors.HTTPException as e:
                print(f"Error: {e}")
                print("Sleeping for 1 minute")
                time.sleep(60)

            requests_made += 1

    def _get_image_urls(self, tweet, all_media):
        """
        Gets the image urls from the tweet
        Each tweet has a list of media keys, those keys can be used to search the media for the correct urls
        :param tweet: The tweet with images we want to get the urls for
        :param all_media: The media from the response from the Twitter API (Sections are removed as they are searched)
        :return: A list of urls to the images in the tweet
        """
        try:
            tweets_media_keys = tweet["attachments"]["media_keys"]  # The media keys associated with this tweet
        except KeyError:
            return []  # If there are no media keys, there are no images in the tweet
        except TypeError:
            return []  # Couldn't find the attachment's keys

        media_urls = []
        # Iterating through all the media to see if any of them match the media keys from the tweet
        # If they do match, that media is removed from the all_media list so future searches are faster
        for media in all_media.copy():
            if media["media_key"] in tweets_media_keys:
                url = media["url"]
                if url is not None:
                    media_urls.append(media["url"])
                all_media.remove(media)

        return media_urls

    def _format_tweet_results(self, res):
        """
        Converts the JSON response from Twitter into a list of dictionaries with the data we want
        :param res: The JSON response from Twitter
        :param download_images: Whether to download the images from the tweets or just save their links
        :return: A list of dictionaries with the data we want
        """
        tweets = []
        no_media = False
        if "media" not in res.includes:
            no_media = True

        all_users = res.includes["users"].copy()

        for i in range(len(res.data)):
            id = res.data[i].id
            text = res.data[i].text

            author_id = res.data[i].author_id
            # Searching through all the users to find the author of this tweet
            author_username = None
            author_name = None
            for user in all_users:
                if user["id"] == author_id:
                    author_username = user["username"]
                    author_name = user["name"]
                    break

            # Public Metrics
            # retweet_count, reply_count, like_count, quote_count, impression_count
            # Only retweet_count has a large variety of values; the rest are almost always 0.
            retweet_count = res.data[i].public_metrics["retweet_count"]

            hashtags = []
            mentions = []
            image_urls = []

            if res.data[i].entities is not None:  # When there are no entities, there are no hashtags, mentions, or urls
                # Getting hashtags
                if "hashtags" in res.data[i].entities:
                    for hashtag in res.data[i].entities["hashtags"]:
                        hashtags.append(hashtag["tag"])

                # Getting mentions
                if "mentions" in res.data[i].entities:
                    for mention in res.data[i].entities["mentions"]:
                        mentions.append(mention["username"])

                # Getting direct image urls
                if not no_media:
                    image_urls = self._get_image_urls(res.data[i], res.includes["media"])

            created_at = res.data[i].created_at

            # Convert date time to a string
            created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")

            tweets.append(
                {
                    "id": id,
                    "text": text,
                    "date": created_at,
                    "author_id": author_id,
                    "author_name": author_name,
                    "author_username": author_username,
                    "retweet_count": retweet_count,
                    "hashtags": hashtags,
                    "mentions": mentions,
                    "image_urls": image_urls,
                    "tweet_url": f"https://twitter.com/{author_username}/status/{id}",
                }
            )
        return tweets

    def _get_single_tweet(self, tweet_id: str):
        """
        https://developer.x.com/en/docs/x-api/tweets/lookup/api-reference/get-tweets-id
        https://docs.tweepy.org/en/stable/client.html#tweepy.Client.get_tweet
        """
        return self.client.get_tweet(tweet_id,
                                     expansions=fields.ALL_EXPANSIONS,
                                     media_fields=fields.ALL_MEDIA_FIELDS,
                                     place_fields=fields.ALL_PLACE_FIELDS,
                                     tweet_fields=fields.ALL_TWEET_FIELDS,
                                     user_fields=fields.ALL_USER_FIELDS,
                                     )

    def _get_multiple_tweets_by_ids(self, tweet_ids: list):
        return self.client.get_tweets(tweet_ids,
                                        expansions=fields.ALL_EXPANSIONS,
                                        media_fields=fields.ALL_MEDIA_FIELDS,
                                        place_fields=fields.ALL_PLACE_FIELDS,
                                        tweet_fields=fields.ALL_TWEET_FIELDS,
                                        user_fields=fields.ALL_USER_FIELDS,
                                        )



if __name__ == "__main__":
    api_key = open("twitter_api/bearer.key", "r").read()
    collector = IDTwitterCollector(api_key)
    
    example = collector.get_single_tweet("1772726192967156095")
    # Write the example to a json file
    json.dump(example.data._json, open("example.json", "w"), indent=4)