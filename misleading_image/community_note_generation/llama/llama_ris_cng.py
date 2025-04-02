import json
import time
import requests
from io import BytesIO
from PIL import Image
import os 

# Import Groq client
from groq import Groq

def generate_community_note(
    tweet_text: str,
    tweet_image: Image,
    ris_results: dict,
    google_ground=False,
    include_ris_thumbnails=False,
    multishot=True,
    temperature=1,
    max_tokens=1024,
    top_p=1,
    rate_limit_seconds=0.1
) -> str:
    """
    Generate a community note using the llama-3.3-70b-versatile model from the Groq API.
    """

    prompt_path = "misleading_image/prompts/community_note_generation_1.txt"
    
    prompt_sections = []
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_sections.append(f.read())

    # Optionally load a multi-shot example prompt (few-shot) if desired
    if multishot:
        with open("misleading_image/prompts/community_note_examples.txt", "r", encoding="utf-8") as f:
            prompt_sections.append(f.read())

    # Construct text from RIS (Reverse Image Search) results
    prompt_sections.append(
        "We ran a reverse image search on the image and found the following matches. "
        "Don't assume these are perfectly related to the original tweet:"
    )

    # Include up to the first 3 matches
    max_matches = min(3, len(ris_results))
    match_counter = 1
    for i in range(max_matches):
        # Each match can have up to 3 context items
        max_contexts = min(3, len(ris_results[i]["image_context"]))
        for mc in range(max_contexts):
            prompt_sections.append(f"# Match {match_counter}")
            prompt_sections.append("Title:")
            prompt_sections.append(ris_results[i]['image_context'][mc]['title'])
            prompt_sections.append("Link:")
            prompt_sections.append(ris_results[i]["image_context"][mc]['link'])
            prompt_sections.append("Snippet:")
            prompt_sections.append(ris_results[i]["image_context"][mc]['snippet'])
            match_counter += 1

        # Download and embed thumbnail text if requested
        if include_ris_thumbnails:
            thumbnail_url = ris_results[i].get('thumbnail')
            if thumbnail_url:
                try:
                    thumbnail_bytes = requests.get(thumbnail_url).content
                    img = Image.open(BytesIO(thumbnail_bytes))
                    prompt_sections.append("Thumbnail:")
                    prompt_sections.append(f"(Embedded thumbnail of size {img.size})")
                except:
                    pass

    prompt_sections.append(
        "# Below is the tweet and image we would like you to write a community note for."
    )
    prompt_sections.append(f"Tweet: {tweet_text}")
    prompt_sections.append("Image:")
    # Provide an image description or similar text if desired
    prompt_sections.append(f"(Embedded tweet image of size {tweet_image.size})")

    # Add final instruction to output the community note
  
    prompt_sections.append("Community Note (reference sources if applicable):")

    # Combine everything into one big prompt
    full_prompt = "\n".join(str(section) for section in prompt_sections)

    # Create a client instance for Groq
    client = Groq(api_key=open("misleading_image/community_note_generation/llama/groq_api.key").read().strip())

    # Set up the streaming chat completion call
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an assistant that helps generate factual community notes."},
            {"role": "user", "content": full_prompt},
        ],
        temperature=temperature,
        max_completion_tokens=max_tokens,
        top_p=top_p,
        stream=True,
        stop=None
    )

    # Collect chunks from the streaming response
    generated_note = []
    for chunk in completion:
        print(chunk.choices[0].delta.content or "", end="")
        # Each chunk includes a delta with partial text. Accumulate them.
        content_piece = chunk.choices[0].delta.content or ""
        generated_note.append(content_piece)

        # Optional short sleep to rate-limit the speed of token streaming
        time.sleep(rate_limit_seconds)

    # Return the entire generated text as a single string
    class Response:
        def __init__(self, text):
            self.text = text
    return Response("".join(generated_note))


def main():
    # Load a sample dataset
    dataset_path = "misleading_image/community_note_generation/test_sets/filtered_tweets_125_with_context.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # Example using the 3rd entry
    instance = dataset[2]
    tweet_text = instance["text"]
    tweet_image_url = instance["image_urls"][0]
    ris_results = instance["reverse_image_search_results"]

    # Download the tweet image
    response = requests.get(tweet_image_url)
    tweet_image = Image.open(BytesIO(response.content))

    # Generate the community note
    note = generate_community_note(
        tweet_text=tweet_text,
        tweet_image=tweet_image,
        ris_results=ris_results,
        google_ground=True,   # or False, depending on your use case
        include_ris_thumbnails=False,
        multishot=True,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        rate_limit_seconds=0.1  # Adjust the sleep time to control streaming speed
    )

    print("\n=== Generated Community Note ===")
    print(note)


if __name__ == "__main__":
    main()
