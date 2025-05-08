import pandas as pd
from .filter_community_notes import filter_community_notes_step
from misleading_image.dataset_updater.step import Step

def put_author_info_in_tweets(tweets, author_info_df):
    """
    Add author information to the tweets based on the author_info_df DataFrame.
    :param tweets: List of tweets (dictionaries) to update.
    :param author_info_df: DataFrame containing author information.
    :return: Updated list of tweets with author information.
    """
    author_info_df = author_info_df.set_index("participantId").to_dict(orient="index")

    for tweet in tweets:
        community_note = tweet.get("community_note")
        author_id = community_note.get("noteAuthorParticipantId")
        if author_id and author_id in author_info_df:
            author_info = author_info_df[author_id].copy()
            author_info.pop("participantId", None)
            tweet["community_note"]["author_information"] = author_info 
        else:
            tweet["community_note"]["author_information"] = None       


    return tweets

def add_note_author_information(checkpoint, authorInfoFile):
    """
    Add author information to the notes in the checkpoint dataset.
    :param checkpoint: The Checkpoint object to update.
    :param authorInfoFile: Path to the TSV file containing the author information.
    run as python -m misleading_image.dataset_updater.update --checkpoint_path="" --step_name="Add Author Information" --kwargs '{"authorInfoFile": ""}'
    """

    if any(step.name == "Add Author Information" for step in checkpoint.executed_steps):
        print("Skipping step as it has already been executed")
        return
    
    tweets = checkpoint.dataset
    author_info_df = pd.read_csv(authorInfoFile, sep="\t")
    tweets = put_author_info_in_tweets(tweets, author_info_df)
    checkpoint.dataset = tweets

add_note_author_information_step = Step(
    name="Add Author Information",
    action=add_note_author_information,
    execution_args=['authorInfoFile', 'checkpoint'],
    preconditions=[filter_community_notes_step],  # Ensure this step runs after filtering community notes
)
    
