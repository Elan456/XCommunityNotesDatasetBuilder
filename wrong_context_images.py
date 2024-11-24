"""
Creates a dataset from the twitter community notes dataset that only contains notes
where the classification is misleading 
"""

import argparse 
import pandas as pd
import numpy as np

import note_filtering

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", help="The input file to filter", default="notes-00000.tsv")
    parser.add_argument("--output_file", help="The output file to write the filtered notes to", default="notes-sample-filtered.tsv")
    args = parser.parse_args()
    
    notes = pd.read_csv(args.input_file, sep="\t")

    try: 
        notes = note_filtering.filter_summary_duplicates(notes)
        notes = note_filtering.filter_classification_not_misinformed(notes)
        notes = note_filtering.filter_misleading_images(notes)
        # print("pre manipulated media filter shape:", notes.shape)
        # notes = note_filtering.filter_mainpulated_media(notes)
        print("pre photo keyword filter shape:", notes.shape)
        notes = note_filtering.filter_contains_photo_or_image_keyword(notes)
        print("post photo keyword filter shape:", notes.shape)
    except ValueError as e:
        print(e)
        exit(1)
    
    notes.to_csv(args.output_file, sep="\t", index=False)
    
    
    # Final shape!
    print("Final shape:", notes.shape)
