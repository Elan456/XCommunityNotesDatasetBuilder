from misleading_image.dataset_updater.step import Step
import json
import pandas as pd
import os

from twitter_api.collector.id_collector import IDTwitterCollector
from misleading_image.community_note_injector import build_community_note_dict, add_community_note_to_json

def collect_tweets(checkpoint):
    """
    Collect tweets from Twitter's API using tweet IDs in the checkpoint dataset.

    :param checkpoint: The Checkpoint object to update."

    run as python -m misleading_image.dataset_updater.update --checkpoint_path="" --step_name="Collect Tweets"
    """

    if any(step.name == "Collect Tweets" for step in checkpoint.executed_steps):
        print("Skipping step as it has already been executed")
        return
    
    notes = pd.DataFrame(checkpoint.dataset)
    if notes.empty:
        print("Checkpoint dataset is empty")
        return

    id_collector = IDTwitterCollector(open("twitter_api/bearer.key").read().strip())
    ids_list = notes["tweetId"].tolist()


    if(len(ids_list) == 0):
        print("No tweet IDs found in the dataset")
        return
    else:
        print("Need to collect", len(ids_list), "tweets")
        all_tweets = []
        for tweets in id_collector.get_tweets_by_ids(ids_list):
            all_tweets.extend(tweets)

    comm_notes = build_community_note_dict(notes_df=notes)
    all_tweets = add_community_note_to_json(tweets=all_tweets, community_note_dict=comm_notes)

    checkpoint.dataset = all_tweets


collect_tweets_step = Step(name="Collect Tweets", action=collect_tweets)