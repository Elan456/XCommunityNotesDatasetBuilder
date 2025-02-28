from checkpoint import Checkpoint
from step import Step
# import wrong_context_community_notes_filter
# from twitter_api.collector.id_collector import IDTwitterCollector
# from misleading_image import add_contextual_or_misleading_image_labels
# from misleading_image import community_note_injector
# from misleading_image import add_topical_category
import json
import os
import pandas as pd
from misleading_image.dememe import remove_meme_text
from PIL import Image
import requests
from io import BytesIO

WRONG_CONTEXT_COMMUNITY_NOTES = "wrong_context_community_notes.tsv"
NOVEL_WRONG_CONTEXT_COMMUNITY_NOTES = "novel_wrong_context_community_notes.tsv"
COMMUNITY_NOTES_TWEETS = "community_notes_tweets.json"
COMMUNITY_NOTES_TWEETS_FINISHED = "community_notes_tweets_finished.flag"

# Combined tweets with their community notes
TWEETS_WITH_COMMUNITY_NOTES = "tweets_with_community_notes.json"

# Contextual or misleading image labels from LLM with the community notes and tweets (concise name)
CONTEXTUAL_OR_MISLEADING_IMAGE_LABELS = "contextual_or_misleading_image_labels.json"

# with topical categories added on, needs community notes, tweet, and images
TWEETS_WITH_TOPICAL_CATEGORIES = "tweets_with_topical_categories.json"

# Final dataset with the existing dataset and the new tweets
FINAL_DATASET = "final_dataset.json"

OOC_COMMUNITY_NOTES = "ooc_community_notes.json"


# Step 1: Filter the community notes
def filter_community_notes(checkpoint, notes_tsv_file):
    """
    Filter the community notes and update the checkpoint dataset.

    :param checkpoint: The Checkpoint object to update.
    :param notes_tsv_file: Path to the TSV file containing the notes.
    """
    output_path = os.path.join(checkpoint.output_directory, WRONG_CONTEXT_COMMUNITY_NOTES)

    # Check if the step has already been executed
    if any(step.name == "Filter Community Notes" for step in checkpoint.executed_steps):
        print("Skipping step 1 as it has already been executed")
        return

    if os.path.exists(output_path):
        print(f"Skipping step 1 as {output_path} already exists")
    else:
        # wrong_context_community_notes_filter.main(notes_tsv_file, output_path)

        notes = pd.read_csv(output_path, sep="\t")
        checkpoint.dataset = notes.to_dict(orient="records")
        print(f"Filtered community notes and saved to {output_path}")

        # Delete the output file after setting the checkpoint data
        os.remove(output_path)


# Step 2: Remove notes already in the dataset
def remove_existing_notes(checkpoint, current_dataset=None, current_checkpoint=None):
    """
    Remove notes that are already in the existing dataset and update the checkpoint dataset.

    :param checkpoint: The Checkpoint object to update.
    :param current_dataset: Path to the current dataset JSON file.
    :param current_checkpoint: The current Checkpoint object.
    """
    if not current_dataset and not current_checkpoint:
        raise ValueError("Either 'current_dataset' or 'current_checkpoint' must be provided")

    # Check if the step has already been executed
    if any(step.name == "Remove Existing Notes" for step in checkpoint.executed_steps):
        print("Skipping step 2 as it has already been executed")
        return

    # Load the existing dataset and extract tweet IDs
    if current_dataset:
        existing_dataset = pd.read_json(current_dataset)
    else:
        existing_dataset = pd.DataFrame(Checkpoint.load(current_checkpoint).dataset)

    existing_tweet_ids = set(existing_dataset["id"])

    # Load the notes dataset
    notes = pd.DataFrame(checkpoint.dataset)
    previous_len = len(notes)

    # Filter out notes that are already in the existing dataset
    notes = notes[~notes["id"].isin(existing_tweet_ids)]
    after_len = len(notes)

    print(f"Removed {previous_len - after_len} notes that were already in the dataset, {after_len} notes remaining")
    assert after_len < previous_len

    # Update the checkpoint dataset
    checkpoint.dataset = notes.to_dict(orient="records")


# Step 3: Collect tweets by IDs
def collect_tweets(checkpoint, **kwargs):
    pass


# Step 4: Inject community notes into tweets
def inject_community_notes(checkpoint, **kwargs):
    pass


# Step 5: Add contextual or misleading image labels
def add_image_labels(checkpoint, **kwargs):
    pass


# Step 6: Add topical categories
def add_topical_categories(checkpoint, **kwargs):
    pass


# Step 7: Combine with existing dataset
def combine_datasets(checkpoint, **kwargs):
    pass

def reverse_image_search(checkpoint, dataset_json=None):
    """
    Perform reverse image search on the dataset images, without dememeing

    :param checkpoint: The Checkpoint object to update.
    :param dataset_json: Path to the JSON file representing the dataset, if a checkpoint is not provided.
    """

    # Check if the step has already
    if any(step.name == "Reverse Image Search" for step in checkpoint.executed_steps):
        print("Skipping step as it has already been executed")
        return

    # Load the dataset from the checkpoint or JSON file
    if dataset_json:
        with open(dataset_json, 'r') as f:
            current_dataset = json.load(f)
    else:
        current_dataset = Checkpoint.load(checkpoint).dataset

    reverseImageSearchResults = []

    # for each tweet, need to send img url to API and get a response
    # store tweetId, imgURL, and API response in a list
    for tweet in current_dataset:
        tweetId = tweet['id']
        imgURL = tweet['image_urls'][0]
        # send imgURL to API and get response
        # store response in reverseImageSearchResults
        response = [
    {
        "position": 1,
        "title": "The New Obama Administration Defense Of Police Militarization: The Boston Bombing",
        "link": "https://www.buzzfeednews.com/article/evanmcsan/the-boston-defense",
        "source": "BuzzFeed News",
        "source_icon": "https://serpapi.com/searches/67b8c688c24d6096bd5718f2/images/fa4176daf8c26db1febd592788b976b52782c6eaee8a4c5a493513438827a106.png",
        "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSGwd_HIFBTsVS8mXIbuiEcXswNFYTl9YtS13YwIlXPqc3Ei6R_",
        "thumbnail_width": 183,
        "thumbnail_height": 275,
        "image": "https://img.buzzfeed.com/buzzfeed-static/static/2014-12/7/23/campaign_images/webdr04/the-new-obama-administration-defense-of-police-mi-2-16197-1418012533-5_big.jpg",
        "image_width": 236,
        "image_height": 355
    },]
        reverseImageSearchResults.append({"tweetId": tweetId, "imgURL": imgURL, "response": response})

        # save reverse image results as a new checkpoint
    checkpoint.dataset = reverseImageSearchResults

def dememe_reverse_image_search(checkpoint, dataset_json=None):
    """
    Perform reverse image search on the dataset images, with dememeing

    :param checkpoint: The Checkpoint object to update.
    :param dataset_json: Path to the JSON file representing the dataset, if a checkpoint is not provided.
    """

    # Check if the step has already
    if any(step.name == "Dememe Reverse Image Search" for step in checkpoint.executed_steps):
        print("Skipping step as it has already been executed")
        return

    # Load the dataset from the checkpoint or JSON file
    if dataset_json:
        with open(dataset_json, 'r') as f:
            current_dataset = json.load(f)
    else:
        current_dataset = Checkpoint.load(checkpoint).dataset

    dememeReverseImageSearchResults = []

    # for each tweet, need to send img url to API and get a response
    # store tweetId, imgURL, and API response in a list
    for tweet in current_dataset:
        tweetId = tweet['id']
        imgURL = tweet['image_urls'][0]
        # convert image to PIL image
        response = requests.get(imgURL)
        my_img = Image.open(BytesIO(response.content))
        # dememe the image
        cleaned_image, cropped_text = remove_meme_text(my_img)
        # host image temporarily

        # send hostedImage URL to API and get response
        # store response in reverseImageSearchResults
        response = [
    {
        "position": 1,
        "title": "The New Obama Administration Defense Of Police Militarization: The Boston Bombing",
        "link": "https://www.buzzfeednews.com/article/evanmcsan/the-boston-defense",
        "source": "BuzzFeed News",
        "source_icon": "https://serpapi.com/searches/67b8c688c24d6096bd5718f2/images/fa4176daf8c26db1febd592788b976b52782c6eaee8a4c5a493513438827a106.png",
        "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSGwd_HIFBTsVS8mXIbuiEcXswNFYTl9YtS13YwIlXPqc3Ei6R_",
        "thumbnail_width": 183,
        "thumbnail_height": 275,
        "image": "https://img.buzzfeed.com/buzzfeed-static/static/2014-12/7/23/campaign_images/webdr04/the-new-obama-administration-defense-of-police-mi-2-16197-1418012533-5_big.jpg",
        "image_width": 236,
        "image_height": 355
    },]
        dememeReverseImageSearchResults.append({"tweetId": tweetId, "removedText": cropped_text, "response": response})

        # save reverse image results as a new checkpoint
    checkpoint.dataset = dememeReverseImageSearchResults

"""
when adding a new feature, need to define a new step before combine datasets, and apply that new step on the current
final dataset. Then, run the new full dataset through to run the new tweets through the entire system and then they will 
be combined.
"""

# Create Step instances
filter_community_notes_step = Step(name="Filter Community Notes", action=filter_community_notes,
                                   execution_args=['notes_tsv_file'])
remove_existing_notes_step = Step(name="Remove Existing Notes", action=remove_existing_notes,
                                  execution_args=['current_dataset', 'current_checkpoint'],
                                  preconditions=[filter_community_notes_step])
reverse_image_search_step = Step(name="Reverse Image Search", action=reverse_image_search, execution_args=['dataset_json', 'checkpoint'], )
dememe_reverse_image_search_step = Step(name="Dememe Reverse Image Search", action=dememe_reverse_image_search, execution_args=['dataset_json', 'checkpoint'], )

