"""
Runs each generation method on the test set and than does a tournament style ranking of the methods, using an additional LLM as the judge.
"""

import misleading_image.community_note_generation as cng 
import pandas as pd 
from .gemini import gemini_multishot_cng
from .gemini import gemini_ris_cng

test_set = cng.get_test_set("12-21-2024/tweets_with_community_notes.json")


# Must build a dataframe with the following columns:
# original cn
# a column for each generation method with the generated cn


