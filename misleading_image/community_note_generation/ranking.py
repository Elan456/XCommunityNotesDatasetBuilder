"""
Runs each generation method on the test set and than does a tournament style ranking of the methods, using an additional LLM as the judge.
"""

import misleading_image.community_note_generation as cng 
import pandas as pd 
from .gemini import gemini_multishot_cng
from .gemini import gemini_ris_cng
from misleading_image.gemini import Gemini
from .generator import generate
from .generation_scorer import rank

try:
   print("Loading in pre-generated test set")
   test_set = pd.read_csv("misleading_image/ranking_test_set.csv")
except FileNotFoundError:
    print("Generating test set")
    test_set = cng.get_test_set("12-21-2024/tweets_with_ris.json")

gemini = Gemini("misleading_image/google.key")

test_set = generate(test_set, gemini_ris_cng.generate_community_note, "gemini_ris_cng", gemini)
test_set.to_csv("misleading_image/ranking_test_set.csv")

test_set = generate(test_set, gemini_ris_cng.generate_community_note, "gemini_ris_cng_gg", gemini, google_ground=True)
test_set.to_csv("misleading_image/ranking_test_set.csv")


test_set = generate(test_set, gemini_multishot_cng.generate_community_note, "gemini_multishot_cng", gemini)
test_set.to_csv("misleading_image/ranking_test_set.csv")

test_set = generate(test_set, gemini_multishot_cng.generate_community_note, "gemini_multishot_cng_gg", gemini, google_ground=True)
test_set.to_csv("misleading_image/ranking_test_set.csv")


# Add a baseline column
test_set["baseline"] = "This tweet is perfectly fine and does not need a community note."



# Run the tournament
results, ranking = rank(test_set, "original_cn", ['gemini_multishot_cng', 'gemini_multishot_cng_gg', 'gemini_ris_cng', 'gemini_ris_cng_gg', 'baseline'])
print(ranking)

# Save to csv
results.to_csv("misleading_image/ranking_results.csv")
ranking.to_csv("misleading_image/ranking.csv")
