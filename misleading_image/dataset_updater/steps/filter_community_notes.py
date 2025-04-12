import os

import pandas as pd

from misleading_image.dataset_updater.step import Step
import wrong_context_community_notes_filter


def filter_community_notes(checkpoint, notes_tsv_file):
    """
    Filter the community notes and update the checkpoint dataset.

    :param checkpoint: The Checkpoint object to update.
    :param notes_tsv_file: Path to the TSV file containing the notes.

    use as python -m misleading_image.dataset_updater.update --checkpoint_path="" --step_name="Filter Community Notes" --kwargs '{"notes_tsv_file": ""}'
    """
    # Check if the step has already been executed
    if any(step.name == "Filter Community Notes" for step in checkpoint.executed_steps):
        print("Skipping step as it has already been executed")
        return
    
    tweets = wrong_context_community_notes_filter.main(notes_tsv_file, return_data=True)

    #make it json serializable
    tweets = tweets.to_dict(orient='records')
    checkpoint.dataset = tweets

filter_community_notes_step = Step(name="Filter Community Notes", action=filter_community_notes, execution_args=['notes_tsv_file', 'checkpoint'], )

# python -m misleading_image.dataset_updater.update --checkpoint_path="" --step_name="Filter Community Notes" --kwargs '{"notes_tsv_file": ""}'