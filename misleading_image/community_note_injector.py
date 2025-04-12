"""
Given a json file with a list of Tweets i.e. {id: , text: , image: , ...}
Adds all the community note info to it as {community note: {}}
"""

import argparse 
import json 
import pandas as pd 


def add_community_note_to_json(tweet_file=None, output_file=None, community_note_dict=None, tweets=None):
    """
    Adds the community note to the json file
    """

    if tweets is None:
        if tweet_file is None:
            raise ValueError("Either tweet_file or tweets must be provided")
        with open(tweet_file, 'r') as f:
            tweets = json.load(f)


    for tweet in tweets:
        tweet_id = tweet['id']
        if tweet_id in community_note_dict:
            tweet['community_note'] = community_note_dict[tweet_id]
        else:
            raise ValueError(f"Tweet id {tweet_id} not found in community notes")


    if output_file:

        with open(output_file, 'w') as f:
            json.dump(tweets, f, indent=4)
    else:
        return tweets


def build_community_note_dict(notes_file=None, notes_df=None):
    """
    Creates a dictionary of tweet_id: community_note from a TSV file
    """


    if notes_df is None:
        if notes_file is None:
            raise ValueError("Either 'notes_file' or 'notes_df' must be provided")
        notes_df = pd.read_csv(notes_file, sep='\t')

    community_note_dict = {}
    unique_tweet_ids = set()

    # Build a dictionary for each line that has every attribute (column) as a key
    # Keys for each community note: noteId	noteAuthorParticipantId	createdAtMillis	tweetId	classification	believable	harmful	validationDifficulty	misleadingOther	misleadingFactualError	misleadingManipulatedMedia	misleadingOutdatedInformation	misleadingMissingImportantContext	misleadingUnverifiedClaimAsFact	misleadingSatire	notMisleadingOther	notMisleadingFactuallyCorrect	notMisleadingOutdatedButNotWhenWritten	notMisleadingClearlySatire	notMisleadingPersonalOpinion	trustworthySources	summary	isMediaNote	twitter_link
    # Basically {tweet_id: {}}
    for index, row in notes_df.iterrows():
        tweet_id = row['tweetId']
        unique_tweet_ids.add(tweet_id)
        community_note_dict[tweet_id] = row.to_dict()

    print("Number of unique tweet ids: ", len(unique_tweet_ids))
    print("Number of community notes: ", len(community_note_dict))

    return community_note_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add community note to json file')
    parser.add_argument('--tweet_file', type=str, help='Input json file')
    parser.add_argument("--notes_file", type=str, help="Input TSV file with community notes")
    parser.add_argument('--output_file', type=str, help='Output json file')
    args = parser.parse_args()

    community_notes_dict = build_community_note_dict(args.notes_file)
    add_community_note_to_json(args.tweet_file, args.output_file, community_notes_dict)
