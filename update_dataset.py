"""
Given a community notes and the current dataset, update the dataset with the new notes.

Steps 
1. Filter the community notes using `note_filtering.py` to get only relevant notes
2. Remove notes that are already in the dataset
3. Give the list of notes to the `id_collector` to get the actual tweets
4. Inject the community notes into the tweets using `community_note_injector.py` to unify the dataset for LLM
5. Run the tweets with the cn into the `add_contextual_or_misleading_image_labels.py` to get the labels
6. Combine this data with the existing dataset to create a new dataset
"""

import pandas as pd
import os
import sys
import json
import re
import argparse

import wrong_context_community_notes_filter
from twitter_api.collector.id_collector import IDTwitterCollector
from misleading_image import add_contextual_or_misleading_image_labels
from misleading_image import community_note_injector

WRONG_CONTEXT_COMMUNITY_NOTES = "wrong_context_community_notes.tsv"
NOVEL_WRONG_CONTEXT_COMMUNITY_NOTES = "novel_wrong_context_community_notes.tsv"
COMMUNITY_NOTES_TWEETS = "community_notes_tweets.json"
COMMUNITY_NOTES_TWEETS_FINISHED = "community_notes_tweets_finished.flag"

# Combined tweets with their community notes
TWEETS_WITH_COMMUNITY_NOTES = "tweets_with_community_notes.json"

# Contextual or misleading image labels from LLM with the community notes and tweets (concise name)
CONTEXTUAL_OR_MISLEADING_IMAGE_LABELS = "contextual_or_misleading_image_labels.json"

# Final dataset with the existing dataset and the new tweets
FINAL_DATASET = "final_dataset.json"

OOC_COMMUNITY_NOTES = "ooc_community_notes.json"



def get_existing_notes_tweet_ids(path_to_dataset_json, path_to_tweets_already_collected=None):
    """
    Get the tweet ids from the existing dataset
    """
    with open(path_to_dataset_json, "r") as f:
        data = json.load(f)
    
    tweet_ids = set()
    for note in data:
        tweet_ids.add(note["id"])

    if path_to_tweets_already_collected:
        with open(path_to_tweets_already_collected, "r") as f:
            already_collected = json.load(f)
            for tweet in already_collected:
                tweet_ids.add(tweet["id"])

    return tweet_ids

def main(args):

    os.makedirs(args.output_directory, exist_ok=True)

    # Step 1: Filter the community notes
    print("\n\nStep 1: Filter the community notes")
    # Skip condition (if file already exists)
    if os.path.exists(args.output_directory + "/" + WRONG_CONTEXT_COMMUNITY_NOTES):
        print(f"Skipping step 1 as {args.output_directory + '/' + WRONG_CONTEXT_COMMUNITY_NOTES} already exists")
    else:
        wrong_context_community_notes_filter.main(args.community_notes, args.output_directory + "/" + WRONG_CONTEXT_COMMUNITY_NOTES)

    #
    # Step 2: Remove notes that are already in the dataset
    #
    print("\n\nStep 2: Remove notes that are already in the dataset")
    notes = None
    # Skip condition (if file already exists)
    if os.path.exists(args.output_directory + "/" + NOVEL_WRONG_CONTEXT_COMMUNITY_NOTES):
        print(f"Skipping step 2 as {args.output_directory + '/' + NOVEL_WRONG_CONTEXT_COMMUNITY_NOTES} already exists")
        notes = pd.read_csv(args.output_directory + "/" + NOVEL_WRONG_CONTEXT_COMMUNITY_NOTES, sep="\t")
    else:
        existing_tweet_ids = get_existing_notes_tweet_ids(args.current_dataset, args.tweets_already_collected)
        notes = pd.read_csv(args.output_directory + "/" + WRONG_CONTEXT_COMMUNITY_NOTES, sep="\t")
        previous_len = len(notes)
        notes = notes[~notes["tweetId"].isin(existing_tweet_ids)]
        after_len = len(notes)
        
        print(f"Removed {previous_len - after_len} notes that were already in the dataset, {after_len} notes remaining")
        assert after_len < previous_len
        
        notes.to_csv(args.output_directory + "/" + NOVEL_WRONG_CONTEXT_COMMUNITY_NOTES, sep="\t", index=False)

    # Step 3: Get the actual tweets
    print("\n\nStep 3: Get the actual tweets")
   
    id_collector = IDTwitterCollector(open("twitter_api/bearer.key").read().strip())
    ids_list = notes["tweetId"].tolist()

    # Remove from the ids_list the ids that are in the tweet_output_file (this step may have been cancelled early during a previous run)
    if os.path.exists(args.output_directory + "/" + COMMUNITY_NOTES_TWEETS):
        with open(args.output_directory + "/" + COMMUNITY_NOTES_TWEETS, "r") as f:
            already_collected = json.load(f)
            already_collected_ids = set([tweet["id"] for tweet in already_collected])
            ids_list = [tweet_id for tweet_id in ids_list if tweet_id not in already_collected_ids]

    if len(ids_list) == 0 or os.path.exists(args.output_directory + "/" + COMMUNITY_NOTES_TWEETS_FINISHED):
        print("All tweets have already been collected")
    else:
        print("Need to collect", len(ids_list), "tweets")
        tweet_output_file = args.output_directory + "/" + COMMUNITY_NOTES_TWEETS

        for tweets in id_collector.get_tweets_by_ids(ids_list):
            print(f"Saving {len(tweets)} tweets to {tweet_output_file}")
            # Write the tweets to the output file
            # Tweets is a list of dictionaries
            
            # Try to load the current output file, and then append the new tweets to it
            all_tweets = []
            if os.path.exists(tweet_output_file):
                with open(tweet_output_file, "r") as f:
                    try:
                        already_captured = json.load(f)
                    except json.JSONDecodeError:  # Empty file
                        already_captured = []
                    all_tweets = already_captured + tweets
            else:
                all_tweets = tweets

            with open(tweet_output_file, "w") as f:
                json.dump(all_tweets, f, indent=4)

            print(f"Collected {len(all_tweets)} out of {len(ids_list)} tweets")

        # Mark the collection as finished
        with open(args.output_directory + "/" + COMMUNITY_NOTES_TWEETS_FINISHED, "w") as f:
            f.write("")


    # Step 4: Inject the community notes into the tweets
    print("\n\nStep 4: Inject the community notes into the tweets")
    if os.path.exists(args.output_directory + "/" + TWEETS_WITH_COMMUNITY_NOTES):
        print(f"Skipping step 4 as {args.output_directory + '/' + TWEETS_WITH_COMMUNITY_NOTES} already exists")
    else:
        notes_dict = community_note_injector.build_community_note_dict(args.output_directory + "/" + NOVEL_WRONG_CONTEXT_COMMUNITY_NOTES)  
        community_note_injector.add_community_note_to_json(tweet_output_file, args.output_directory + "/" + TWEETS_WITH_COMMUNITY_NOTES, notes_dict)

    # Step 5: Run the tweets with the cn into the `add_contextual_or_misleading_image_labels.py` to get the labels
    print ("\n\nStep 5: Use LLM to get the contextual or misleading image labels")
    if os.path.exists(args.output_directory + "/" + CONTEXTUAL_OR_MISLEADING_IMAGE_LABELS):
        print(f"Skipping step 5 as {args.output_directory + '/' + CONTEXTUAL_OR_MISLEADING_IMAGE_LABELS} already exists")
    else:
        add_contextual_or_misleading_image_labels.main(args.output_directory + "/" + TWEETS_WITH_COMMUNITY_NOTES, args.output_directory + "/" + CONTEXTUAL_OR_MISLEADING_IMAGE_LABELS)

    # Step 6: Combine this data with the existing dataset to create a new dataset
    print("\n\nStep 6: Combine this data with the existing dataset to create a new dataset")
    if os.path.exists(args.output_directory + "/" + FINAL_DATASET):
        print(f"Skipping step 6 as {args.output_directory + '/' + FINAL_DATASET} already exists")
    else:
        with open(args.current_dataset, "r") as f:
            existing_data = json.load(f)

        with open(args.output_directory + "/" + CONTEXTUAL_OR_MISLEADING_IMAGE_LABELS, "r") as f:
            new_data = json.load(f)

        final_data = existing_data + new_data
        with open(args.output_directory + "/" + FINAL_DATASET, "w") as f:
            json.dump(final_data, f, indent=4)

    # Step 7: Create a contextual only dataset
    print("\n\nStep 7: Create a contextual only dataset")
    if os.path.exists(args.output_directory + "/" + OOC_COMMUNITY_NOTES):
        print(f"Skipping step 7 as {args.output_directory + '/' + OOC_COMMUNITY_NOTES} already exists")
    else:
        # load the final dataset filter if llm_image_classification is contextual e.g. ""llm_image_classification": "contextual","
        with open(args.output_directory + "/" + FINAL_DATASET, "r") as f:
            final_data = json.load(f)
        items = []
        id_set = set()
        for item in final_data:
            if item.get("llm_image_classification", "unknown") == "contextual":
                items.append(item)
                id_set.add(item["id"])
        with open(args.output_directory + "/" + OOC_COMMUNITY_NOTES, "w") as f:
            json.dump(items, f, indent=4)
        print(f"Saved {len(items)} contextual tweets to {args.output_directory + '/' + OOC_COMMUNITY_NOTES}")

        assert len(items) == len(id_set)







if __name__ == "__main__":

    # Need path to the community notes and the current dataset
    parser = argparse.ArgumentParser(description='Update dataset with community notes')
    parser.add_argument('--community_notes', type=str, help='Path to the community notes')
    parser.add_argument('--current_dataset', type=str, help='Path to the current dataset')
    parser.add_argument('--tweets_already_collected', type=str, help='Path to a json of tweets already collected')
    parser.add_argument('--output_directory', type=str, help='Path to save the updated dataset')
    args = parser.parse_args()

    main(args)


