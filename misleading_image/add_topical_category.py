"""
Given a json file with tweets and their community notes i.e. 
[{id: , text: , community_note: {summary: ,....}}, ...]

Uses an LLM to add topical categories to each tweet
"""

import argparse
import json 
from .twc import TweetWithContext
from .gemini import gemini_add_topical_categories
from tqdm import tqdm 

def main(tweet_json_file, output_json_file):
    with open(tweet_json_file, 'r') as f:
        tweets = json.load(f) # [:10]

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
    tweet_objs = gemini_add_topical_categories(tweet_objs)

    for twc in tweet_objs:
        tweet_index = None 
        for i, tweet in enumerate(tweets):
            if tweet['id'] == twc.id:
                tweet_index = i
                break

        if tweet_index is None:
            raise ValueError(f"Tweet id {twc.id} not found in tweets")
        
        tweets[tweet_index]['topical_categories'] = twc.topical_categories
        tweets[tweet_index]['full_topical_categories_response'] = twc.full_topical_category_response
        

    with open(output_json_file, 'w') as f:
        json.dump(tweets, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add LLM image classification to json file')
    parser.add_argument('--tweet_file', type=str, help='Input json file')
    parser.add_argument('--output_file', type=str, help='Output json file')
    args = parser.parse_args()

    main(args.tweet_file, args.output_file)