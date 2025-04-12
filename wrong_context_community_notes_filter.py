"""
Creates a dataset from the twitter community notes dataset that only contains notes
where the classification is misleading 
"""

import argparse 
import pandas as pd
import numpy as np

import note_filtering
def main(input_file, output_file=None, return_data=False):
    """
    Filters the notes dataset and either writes the filtered data to a file or returns it as a DataFrame.

    :param input_file: Path to the input file to filter.
    :param output_file: Path to the output file to write the filtered notes to (optional).
    :param return_data: If True, returns the filtered DataFrame instead of writing to a file.
    :return: The filtered DataFrame if return_data is True, otherwise None.
    """
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
    
    if return_data:
        # Return the filtered DataFrame instead of writing to a file
        return notes
    
    if output_file:
        # Write the filtered DataFrame to the specified output file
        notes.to_csv(output_file, sep="\t", index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", help="The input file to filter", default="notes-00000.tsv")
    parser.add_argument("--output_file", help="The output file to write the filtered notes to", default="notes-sample-filtered.tsv")
    args = parser.parse_args()
    
    main(args.input_file, args.output_file)
