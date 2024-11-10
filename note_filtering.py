import pandas as pd 
import numpy as np


def filter_classification_not_misinformed(notes):
    """
    Filter out notes that are not misinformed
    """
    
    notes = notes[notes["classification"] != "NOT_MISLEADING"]
    return notes

def filter_misleading_images(notes):
    """
    Keeps notes where isMedia is True and misleadingMissingImportantContext is True
    """

    notes = notes[notes["isMediaNote"] == 1]
    if len(notes) == 0:
        raise ValueError("No notes with isMediaNote == 1")

    notes = notes[notes["misleadingMissingImportantContext"] == 1]
    if len(notes) == 0:
        raise ValueError("No notes with misleadingMissingImportantContext == 1 AND isMediaNote == 1")

    return notes

def filter_mainpulated_media(notes):
    """
    Remove notes where the note maker labeled the note as manipulated media
    """

    notes = notes[notes["misleadingManipulatedMedia"] == 0]
    if len(notes) == 0:
        raise ValueError("No notes with misleadingManipulatedMedia == 0")

    return notes





if __name__ == "__main__":


    # load the tsv "notes-00000.tsv"
    notes = pd.read_csv("notes-sample.tsv", sep="\t")
    notes = filter_classification_not_misinformed(notes)


    print(notes.head())