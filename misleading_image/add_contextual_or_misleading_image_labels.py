"""
Given a json file with tweets and their community notes i.e. 
[{id: , text: , community_note: {summary: ,....}}, ...]

Uses an LLM to descide if each tweet's image is contextual or is inherently misleading
A contextual image isn't intended to mislead, but can be taken out of context if the tweet text doesn't provide enough information or 
reframes the image in a way that is misleading. A misleading image is an image that is intended to mislead the viewer on it's own 
regardless of the tweet text.

Outputs a JSON file with all the same information but an addded key `llm_image_classification` with the value of either "contextual" or "misleading"
"""

import argparse
import json 
from .twc import TweetWithContext
from .gemini import gemini_filter_misleading_images
from tqdm import tqdm 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add LLM image classification to json file')
    parser.add_argument('--tweet_file', type=str, help='Input json file')
    parser.add_argument('--output_file', type=str, help='Output json file')
    args = parser.parse_args()

    with open(args.tweet_file, 'r') as f:
        tweets = json.load(f)[:10]

    # Remove tweets without images
    tweets = [tweet for tweet in tweets if tweet['image_urls']]

    tweet_objs = []
    iterator = tqdm(tweets)
    iterator.set_description("Loading tweets with images")
    for tweet in iterator:
        # Check that the tweet has an image
        if not tweet['image_urls']:
            print(f"Tweet id {tweet['id']} does not have an image, image_urls: {tweet['image_urls']}, skipping...")
            continue

        tweet_obj = TweetWithContext(tweet['text'], tweet['image_urls'][0], tweet['community_note']['summary'], tweet['id'])
        if not tweet_obj.image:
            print(f"Tweet id {tweet['id']} image could not be loaded, skipping...")
            continue
        tweet_objs.append(tweet_obj)

    # Adding the LLM classification to each tweet object
    tweet_objs = gemini_filter_misleading_images(tweet_objs)

    # Iterate through each tweet_obj and update the tweet json with the classification

    # zip   a [1, 2, 3] and b['a', 'b', 'c'] -> [(1, 'a'), (2, 'b'), (3, 'c')]
    # 


    for twc in tweet_objs:
        tweet_index = None 
        for i, tweet in enumerate(tweets):
            if tweet['id'] == twc.id:
                tweet_index = i
                break

        if tweet_index is None:
            raise ValueError(f"Tweet id {twc.id} not found in tweets")
        
        tweets[tweet_index]['llm_image_classification'] = twc.llm_image_classification
        tweets[tweet_index]['full_llm_image_response'] = twc.full_llm_image_response
        

    with open(args.output_file, 'w') as f:
        json.dump(tweets, f, indent=4)