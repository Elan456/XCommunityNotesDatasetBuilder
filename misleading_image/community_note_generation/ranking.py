"""
Runs each generation method on the test set and than does a tournament style ranking of the methods, using an additional LLM as the judge.
"""

import misleading_image.community_note_generation as cng 
import pandas as pd 
from .gemini import gemini_cng
from .gemini import gemini_ris_cng
from .gemini import gemini_rephrase
from misleading_image.gemini import Gemini
from .generator import generate
from .gcn_scorer import rank
from .llama import llama_ris_cng

# test_set_path = "misleading_image/community_note_generation/test_sets/filtered_contextual_sample_tweets.json"
test_set_path = "misleading_image/community_note_generation/test_sets/3-28-2025/filtered_tweets_125_with_context.json"
gen_path = test_set_path.replace(".json", "_cng.parquet")

try:
   print("Loading in pre-generated test set from: ", gen_path)
   test_set = pd.read_parquet(gen_path)
   # Remove unnamed index column
   test_set = test_set.loc[:, ~test_set.columns.str.contains('^Unnamed')]
except FileNotFoundError:
    print("File not found, Generating test set")
    test_set = cng.get_test_set(test_set_path, size=25)

gemini = Gemini("misleading_image/google.key")

test_set = generate(test_set, gemini_ris_cng.generate_community_note, "gemini_ris_dm", gemini, google_ground=False, dememe=True)
test_set.to_parquet(gen_path)

test_set = generate(test_set, gemini_ris_cng.generate_community_note, "gemini_ris_dm_gg", gemini, google_ground=True, dememe=True)
test_set.to_parquet(gen_path)

test_set = generate(test_set, gemini_ris_cng.generate_community_note, "gemini_ris", gemini)
test_set.to_parquet(gen_path)

test_set = generate(test_set, gemini_ris_cng.generate_community_note, "gemini_ris_gg", gemini, google_ground=True)
test_set.to_parquet(gen_path)

# test_set = generate(test_set, gemini_ris_cng.generate_community_note, "gemini_ris_gg_nms", gemini, google_ground=True, multishot=False)
# test_set.to_parquet(gen_path)


# test_set = generate(test_set, gemini_cng.generate_community_note, "gemini", gemini)
# test_set.to_parquet(gen_path)

test_set = generate(test_set, gemini_cng.generate_community_note, "gemini_gg", gemini, google_ground=True)
test_set.to_parquet(gen_path)

test_set = generate(test_set, llama_ris_cng.generate_community_note, "llama_ris", gemini)
test_set.to_parquet(gen_path)

test_set = generate(test_set, gemini_rephrase.generate_community_note, "pos_baseline", gemini)
test_set.to_parquet(gen_path)


# Add a baseline column
test_set["neg_baseline"] = "This tweet is perfectly fine and does not need a community note."

# Run the tournament
results, ranking = rank(test_set, "original_cn", 
                       ["gemini_ris_dm", "gemini_ris_dm_gg", "gemini_ris", "gemini_ris_gg", "gemini_gg", "pos_baseline", "neg_baseline", "llama_ris"],
                       #  ['gemini_ris_dm', "gemini_ris"],
                        count=100)
print(ranking)

# Save to csv
results.to_csv(test_set_path.replace(".json", "_results.csv"))
ranking.to_csv(test_set_path.replace(".json", "_ranking.csv"))
