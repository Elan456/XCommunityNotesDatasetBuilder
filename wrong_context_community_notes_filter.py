"""
Creates a dataset from the twitter community notes dataset that only contains notes
where the classification is misleading 
"""

import argparse 
import pandas as pd
import numpy as np

import note_filtering

def main(input_file, output_file):
    notes = pd.read_csv(input_file, sep="\t")
    
    try: 
        notes = note_filtering.filter_summary_duplicates(notes)
        notes = note_filtering.filter_classification_not_misinformed(notes)
        notes = note_filtering.filter_misleading_images(notes)
        notes = note_filtering.filter_mainpulated_media(notes)
        notes = note_filtering.filter_contains_photo_or_image_keyword(notes)
        notes = note_filtering.add_twitter_link_column(notes)
    except ValueError as e:
        print(e)
        exit(1)
    
    notes.to_csv(output_file, sep="\t", index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", help="The input file to filter", default="notes-00000.tsv")
    parser.add_argument("--output_file", help="The output file to write the filtered notes to", default="notes-sample-filtered.tsv")
    args = parser.parse_args()
    
    main(args.input_file, args.output_file)
