import pandas as pd
from .filter_community_notes import filter_community_notes_step
from misleading_image.dataset_updater.step import Step

def add_note_status(tweets, notes_status_df):
    """
    Add note status to the notes in the checkpoint dataset.
    :param checkpoint: The Checkpoint object to update.
    :param notes_status_df: DataFrame containing the note status information.
    :return: Updated list of tweets with note status.
    """

    note_status_df = notes_status_df.set_index("noteId").to_dict(orient="index")

    for tweet in tweets:
        community_note = tweet.get("community_note")
        note_id = community_note.get("noteId")
        if note_id and note_id in note_status_df:
            note_status = note_status_df[note_id].copy()
            for field in ["noteId", "noteAuthorParticipantId", "createdAtMillis"]:
                note_status.pop(field, None)
            tweet["community_note"]["note_status_info"] = note_status
        else:
            tweet["community_note"]["note_status_info"] = None

    return tweets


def add_note_status_information(checkpoint, noteStatusFile):
    """
    Add note status to the notes in the checkpoint dataset.
    :param checkpoint: The Checkpoint object to update.
    :param noteStatusFile: Path to the TSV file containing the note status information.
    run as python -m misleading_image.dataset_updater.update --checkpoint_path="" --step_name="Add Note Status" --kwargs '{"noteStatusFile": ""}'
    """

    if any(step.name == "Add Note Status Information" for step in checkpoint.executed_steps):
        print("Skipping step as it has already been executed")
        return
    
    tweets = checkpoint.dataset
    notes_status_df = pd.read_csv(noteStatusFile, sep="\t", low_memory=False)
    tweets = add_note_status(tweets, notes_status_df)
    checkpoint.dataset = tweets

add_note_status_step = Step(
    name="Add Note Status Information",
    action=add_note_status_information,
    execution_args=['noteStatusFile', 'checkpoint'],
    preconditions=[filter_community_notes_step],  # Ensure this step runs after filtering community notes
)

    
