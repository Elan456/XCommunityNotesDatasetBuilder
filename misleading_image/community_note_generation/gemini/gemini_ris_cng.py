from misleading_image.gemini import Gemini
from PIL import Image
import requests
from io import BytesIO
import json 


def generate_community_note(tweet_text, tweet_image: Image, ris_results: dict, gemini: Gemini, google_ground = False, include_ris_thumbnails=False, multishot=True) -> str:
    prompt = []

    if google_ground:
        prompt_path = "misleading_image/prompts/community_note_generation_grounding_1.txt"
    else:
        prompt_path = "misleading_image/prompts/community_note_generation_1.txt"

    with open(prompt_path) as f:
        prompt.append(f.read())

    if multishot:
        with open("misleading_image/prompts/community_note_examples.txt") as f:
            prompt.append(f.read())

    # Take the first 3 matches
    prompt.append("We ran a reverse image search on the image and found the following matches, don't assume these are perfectly related to the original tweet:")
    for i in range(min(3, len(ris_results))):
        for mc in range(min(3, len(ris_results[i]["image_context"]))):
            prompt.append(f"# Match {mc + i * 3 + 1}")
            prompt.append("Title:")
            prompt.append(ris_results[i]['image_context'][mc]['title'])
            
            prompt.append("Link:")
            prompt.append(ris_results[i]["image_context"][mc]['link'])

            prompt.append("Snippet:")
            prompt.append(ris_results[i]["image_context"][mc]['snippet'])

        # Download thumbnail
        # Example: https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcR1_U0QyWS8IYr4VzfVX9CSvV_5NCeOvkvejcvNWuppNrJD4VEJ
        if include_ris_thumbnails:
            thumbnail = requests.get(ris_results[i]['thumbnail'])
            # convert to PIL image
            img = Image.open(BytesIO(thumbnail.content))
            prompt.append("Thumbnail: ")
            prompt.append(img)

    prompt.append("# Below is the tweet and image we would like you to write a community note for.")

    prompt.append("Tweet: " + tweet_text)
    prompt.append("Image: ")
    prompt.append(tweet_image)

    # Need the word "grounding" in the prompt to use Google grounding
    if not google_ground:
        prompt.append("Community Note (reference sources if applicable):")
    else:
        prompt.append("Google Grounded Community Note:")

    # print("Final prompt:", prompt)

    # print("Prompt:", prompt)

    response = gemini.generate(prompt, google_ground=google_ground)
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