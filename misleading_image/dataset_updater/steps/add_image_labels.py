from misleading_image.dataset_updater.step import Step
from misleading_image.add_contextual_or_misleading_image_labels import main as add_contextual_or_misleading_image_labels
import pandas as pd

def add_image_labels(checkpoint):
    """
    Add labels of 'contexutal' or 'misleading' to the images in the dataset.

    run as python -m misleading_image.dataset_updater.update --checkpoint_path="" --step_name="Add Image Labels"
    """

    if any(step.name== "Add Image Label" for step in checkpoint.executed_steps):
        print("Existing step already executed")
        return
    

    existing_dataset = checkpoint.dataset

    tweets_with_labels = add_contextual_or_misleading_image_labels(existing_dataset, return_output=True)
    tweets_with_labels = [tweet for tweet in tweets_with_labels if 'llm_image_classification' in tweet]

    # go through and remove any tweets that do not have labels
    checkpoint.dataset = tweets_with_labels


add_image_labels_step = Step(name="Add Image Labels", action=add_image_labels)

