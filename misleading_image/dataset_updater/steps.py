from XCommunityNotesDatasetBuilder.misleading_image.dataset_updater.checkpoint import Checkpoint
from step import Step
from XCommunityNotesDatasetBuilder import wrong_context_community_notes_filter
from XCommunityNotesDatasetBuilder.twitter_api.collector.id_collector import IDTwitterCollector
from XCommunityNotesDatasetBuilder.misleading_image import add_contextual_or_misleading_image_labels
from XCommunityNotesDatasetBuilder.misleading_image import community_note_injector
from XCommunityNotesDatasetBuilder.misleading_image import add_topical_category
import json
import os
import pandas as pd

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
def filter_community_notes(checkpoint, **kwargs):
    """
    Filter the community notes and update the checkpoint dataset.

    :param checkpoint: The Checkpoint object to update.
    :param kwargs: Additional arguments, expecting 'notes_tsv_file'.
    """
    notes_tsv_file = kwargs.get('notes_tsv_file')
    if not notes_tsv_file:
        raise ValueError("notes_tsv_file must be provided in kwargs")

    output_path = os.path.join(checkpoint.output_directory, WRONG_CONTEXT_COMMUNITY_NOTES)

    # Check if the step has already been executed
    if any(step.name == "Filter Community Notes" for step in checkpoint.executed_steps):
        print("Skipping step 1 as it has already been executed")
        return

    if os.path.exists(output_path):
        print(f"Skipping step 1 as {output_path} already exists")
    else:
        wrong_context_community_notes_filter.main(notes_tsv_file, output_path)

        notes = pd.read_csv(output_path, sep="\t")
        checkpoint.dataset = notes.to_dict(orient="records")
        print(f"Filtered community notes and saved to {output_path}")

        # Delete the output file after setting the checkpoint data
        os.remove(output_path)


# Step 2: Remove notes already in the dataset
def remove_existing_notes(checkpoint, **kwargs):
    """
    Remove notes that are already in the existing dataset and update the checkpoint dataset.

    :param checkpoint: The Checkpoint object to update.
    :param kwargs: Additional arguments, expecting 'current_dataset' or 'current_checkpoint'.
    """
    current_dataset_path = kwargs.get('current_dataset')
    current_checkpoint = kwargs.get('current_checkpoint')

    if not current_dataset_path and not current_checkpoint:
        raise ValueError("Either 'current_dataset' or 'current_checkpoint' must be provided in kwargs")

    # Check if the step has already been executed
    if any(step.name == "Remove Existing Notes" for step in checkpoint.executed_steps):
        print("Skipping step 2 as it has already been executed")
        return

    else:
        # Load the existing dataset and extract tweet IDs
        if current_dataset_path:
            existing_dataset = pd.read_json(current_dataset_path)
        else:
            existing_dataset = pd.DataFrame(current_checkpoint.dataset)

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
