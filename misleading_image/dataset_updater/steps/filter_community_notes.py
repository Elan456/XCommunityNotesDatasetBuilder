import os

import pandas as pd

from misleading_image.dataset_updater.step import Step

WRONG_CONTEXT_COMMUNITY_NOTES = "wrong_context_community_notes.tsv"


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

filter_community_notes_step = Step(name="Filter Community Notes", action=filter_community_notes)