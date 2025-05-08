import pandas as pd
from .filter_community_notes import filter_community_notes_step
from misleading_image.dataset_updater.step import Step

def remove_existing_notes(checkpoint, current_dataset=None, current_checkpoint=None):
    """
    Remove notes that are already in the existing dataset and update the checkpoint dataset.

    :param checkpoint: The Checkpoint object to update.
    :param current_dataset: Path to the current dataset JSON file.
    :param current_checkpoint: The current Checkpoint object.

    run as python -m misleading_image.dataset_updater.update --checkpoint_path="" --step_name="Remove Existing Notes" --kwargs '{"current_dataset": "", "current_checkpoint": ""}'
    """

    # Check if the step has already been executed
    if any(step.name == "Remove Existing Notes" for step in checkpoint.executed_steps):
        print("Skipping step as it has already been executed")
        return

    # Load the existing dataset and extract tweet IDs
    if current_dataset:
        existing_dataset = pd.read_json(current_dataset)
    elif current_checkpoint:
        existing_dataset = pd.DataFrame(current_checkpoint.dataset)
    else:
        existing_dataset = pd.DataFrame(columns=["id"])

    #print length of existing_dataset["id"]
    existing_tweet_ids = set(existing_dataset["id"])
    print(f"Existing dataset has {len(existing_tweet_ids)} tweet IDs")

    # Load the notes dataset
    notes = pd.DataFrame(checkpoint.dataset)

    previous_len = len(notes)

    # Filter out notes that are already in the existing dataset
    notes = notes[~notes["tweetId"].isin(existing_tweet_ids)]
    #remove any duplicates
    notes = notes.drop_duplicates(subset=["tweetId"])
    after_len = len(notes)

    print(f"Removed {previous_len - after_len} notes that were already in the dataset, {after_len} notes remaining")
    assert after_len <= previous_len

    # Update the checkpoint dataset
    checkpoint.dataset = notes.to_dict(orient="records")


remove_existing_notes_step = Step(name="Remove Existing Notes", action=remove_existing_notes,
                                  execution_args=['current_dataset', 'current_checkpoint'],
                                  preconditions=[filter_community_notes_step])