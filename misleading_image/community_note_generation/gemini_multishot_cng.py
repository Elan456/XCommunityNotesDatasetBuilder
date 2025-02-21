"""
Given a few examples of tweet text + image + community note summary:
Will generate a LLM community note summary for a new tweet text + image
"""

import argparse 
from ..gemini import Gemini
import json 
import random
from ..twc import TweetWithContext
import time 

def generate_community_note(tweet_text, tweet_image, gemini: Gemini, google_ground: bool) -> str:
    prompt = []

    if google_ground:
        prompt_path = "misleading_image/prompts/community_note_generation_grounding_1.txt"
    else:
        prompt_path = "misleading_image/prompts/community_note_generation_1.txt"

    with open(prompt_path) as f:
        prompt.append(f.read())

    prompt.append("Tweet: " + tweet_text)
    prompt.append("Image: ")
    prompt.append(tweet_image)

    # Need the word "grounding" in the prompt to use Google grounding
    if not google_ground:
        prompt.append("Community Note:")
    else:
        prompt.append("Google Grounded Community Note:")

    # print("Final prompt:", prompt)

    response = gemini.generate(prompt, google_ground=google_ground)
    return response

def main(args):
    # load the dataset with json
    with open(args.dataset, "r") as f:
        dataset = json.load(f)

    # randomly select examples to put in the prompt
    st = time.time()
    while True:
        example_indices = random.sample(range(len(dataset)), args.example_count)
        
        # Check that they all have image_urls len > 0
        if not all(len(dataset[i]['image_urls']) > 0 for i in example_indices):
            continue

        # randomly select examples to test the model on
        available_indices = list(set(range(len(dataset))) - set(example_indices))
        test_indices = random.sample(available_indices, args.test_count)

        if all(len(dataset[i]['image_urls']) > 0 for i in test_indices):
            break

        if time.time() - st > 10:
            print("Couldn't find enough examples with image urls")
            return

    gemini = Gemini("misleading_image/google.key")
    output_json = []

    for i in test_indices:
        T = TweetWithContext(
            dataset[i]['text'],
            dataset[i]['image_urls'][0],
            dataset[i]['community_note']['summary']
        )
        response = generate_community_note(T, gemini, args.google_ground)
        print("Generated community note for tweet index:", i)
        print(response.text)

        # Append to a file the llm cn, and the actual cn
        with open(f"misleading_image/generated_community_notes_{i}.txt", "w") as f:
            f.write("Generated CN: " + response.text + "\n")
            f.write(str(response)+ "\n")
            f.write("Grounding metadata from candidate 0: " + str(response.candidates[0].grounding_metadata))

            # Remove non-ascii characters
            T.community_note = ''.join([i if ord(i) < 128 else ' ' for i in T.community_note])

            f.write("\n===============================\n\n")
            f.write("Actual CN: " + T.community_note + "\n")
            f.write("\n")

        out_dict = dataset[i]
        out_dict['llm_community_note'] = response.text
        output_json.append(out_dict) 

    # Save the output json
    with open("misleading_image/generated_community_notes.json", "w") as f:
        json.dump(output_json, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a community note summary for a tweet")
    parser.add_argument("--dataset", type=str, help="Path to the dataset with community notes, tweet text, and image paths", required=True)
    parser.add_argument("--example_count", type=int, help="How many examples to randomly select from the dataset and put in the prompt", default=3)
    parser.add_argument("--test_count", type=int, help="How many instances to randomly select from the dataset and test the model on", default=3)
    parser.add_argument("--google_ground", type=bool, help="Whether Gemini uses Google grounding https://ai.google.dev/gemini-api/docs/grounding?lang=python", default=True)
    args = parser.parse_args()
    
    main(args)