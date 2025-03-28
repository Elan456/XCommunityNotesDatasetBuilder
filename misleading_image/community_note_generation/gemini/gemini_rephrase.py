"""
Generates a community note by simply rephrasing the original community note. 
"""

from misleading_image.gemini import Gemini
from PIL import Image
import requests
from io import BytesIO
import json 


def generate_community_note(tweet_text, tweet_image: Image, original_cn: str, gemini: Gemini) -> str:
    prompt = []

  
    prompt_path = "misleading_image/prompts/community_note_generation_1.txt"

    with open(prompt_path) as f:
        prompt.append(f.read())

    prompt.append("# Below is the tweet and image we would like you to write a community note for.")

    prompt.append("Tweet: " + tweet_text)
    prompt.append("Image: ")
    prompt.append(tweet_image)

    prompt.append("Below is the original community note, takes facts and details from this note to write a new one. Simply rephrase the original note.")
    prompt.append("Original Community Note:")
    prompt.append(original_cn)

    response = gemini.generate(prompt)
    return response


def main():
    # Hard coded test
    dataset = json.load(open("12-21-2024/tweets_with_ris.json"))

    instance = dataset[2]
    tweet_text = instance['text']
    tweet_image = instance['image_urls'][0]
    ris_results = instance['reverse_image_search_results']
    
    gemini = Gemini("misleading_image/google.key")

    tweet_image = Image.open(BytesIO(requests.get(tweet_image).content))
    response = generate_community_note(tweet_text, tweet_image, ris_results, gemini, google_ground=True, dememe=False)
    print(response.text)

if __name__ == "__main__":
    main()