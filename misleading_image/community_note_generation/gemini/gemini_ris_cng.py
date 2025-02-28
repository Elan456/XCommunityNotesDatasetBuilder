from misleading_image.gemini import Gemini
from PIL import Image
import requests
from io import BytesIO
import json 


def generate_community_note(tweet_text, tweet_image: Image, ris_results: dict, gemini: Gemini, google_ground: bool, dememe: bool, include_ris_thumbnails=False) -> str:
    prompt = []

    if google_ground:
        prompt_path = "misleading_image/prompts/community_note_generation_grounding_1.txt"
    else:
        prompt_path = "misleading_image/prompts/community_note_generation_1.txt"

    with open(prompt_path) as f:
        prompt.append(f.read())

    # Insert reverse image search results 
    matches = ris_results["visual_matches"]
    # Take the first 3 matches
    prompt.append("We ran a reverse image search on the image and found the following matches, don't assume these are perfectly related to the original tweet:")
    for i in range(max(3, len(matches))):
        prompt.append(f"# Match {i+1}")
        prompt.append("Title:")
        prompt.append(matches[i]['title'])
        
        prompt.append("Source:")
        prompt.append(matches[i]['source'])

        prompt.append("Link:")
        prompt.append(matches[i]['link'])

        # Download thumbnail
        # Example: https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcR1_U0QyWS8IYr4VzfVX9CSvV_5NCeOvkvejcvNWuppNrJD4VEJ
        if include_ris_thumbnails:
            thumbnail = requests.get(matches[i]['thumbnail'])
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
        prompt.append("Community Note:")
    else:
        prompt.append("Google Grounded Community Note:")

    # print("Final prompt:", prompt)

    print("Prompt:", prompt)

    response = gemini.generate(prompt, google_ground=google_ground)
    return response


def main():
    # Hard coded test
    dataset = json.load(open("12-21-2024/tweets_with_community_notes.json"))

    instance = dataset[2]
    tweet_text = instance['text']
    tweet_image = instance['image_urls'][0]
    print(instance['tweet_url'])
    ris_results = {
  "search_metadata": {
    "id": "6380ad5dde983400b1fa6938",
    "status": "Success",
    "json_endpoint": "https://serpapi.com/searches/f6000d11bb444c9d/6380ad5dde983400b1fa6938.json",
    "created_at": "2025-01-03 01:10:13 UTC",
    "processed_at": "2025-01-03 01:10:13 UTC",
    "google_lens_url": "https://lens.google.com/uploadbyurl?url=https://i.imgur.com/HBrB8p0.png",
    "raw_html_file": "https://serpapi.com/searches/f6000d11bb444c9d/6380ad5dde983400b1fa6938.html",
    "total_time_taken": 2.75
  },
  "search_parameters": {
    "engine": "google_lens",
    "url": "https://i.imgur.com/HBrB8p0.png"
  },
  "visual_matches": [
    {
      "position": 1,
      "title": "Danny DeVito — Wikipèdia",
      "link": "https://en.wikipedia.org/wiki/Danny_DeVito",
      "source": "Wikipedia",
      "source_icon": "https://serpapi.com/searches/6777d9c3c3b5a0ac7f1a42bc/images/a010fa01d135674248e5206802a18fa9a02a9ee7c2eacd0e143b39fa6fe2c735.png",
      "thumbnail": "https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcR1_U0QyWS8IYr4VzfVX9CSvV_5NCeOvkvejcvNWuppNrJD4VEJ",
      "thumbnail_width": 245,
      "thumbnail_height": 206,
      "image": "https://upload.wikimedia.org/wikipedia/commons/2/21/Danny_DeVito_by_Gage_Skidmore.jpg",
      "image_width": 2216,
      "image_height": 1864
    },
    {
      "position": 2,
      "title": "Reveal all about Jackie Jackson - YouTube",
      "link": "https://www.youtube.com/watch?v=DijekY9jYAk",
      "source": "YouTube",
      "source_icon": "https://serpapi.com/searches/6777d9c3c3b5a0ac7f1a42bc/images/a010fa01d13567427aa89992990fe40fa1120f0c92a3b9855910d44e3f059421.png",
      "thumbnail": "https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcTaqmC3TCaRbjlCbE7RkwAjYTmUoAHdaM3HH9-q0Ja8PSOdeeKe",
      "thumbnail_width": 168,
      "thumbnail_height": 299,
      "image": "https://i.ytimg.com/vi/URMSh0gO_48/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLALdJhqpbCqydHCAjSh_0_jx_CIcg",
      "image_width": 386,
      "image_height": 686
    },
    {
      "position": 3,
      "title": "✨Wiccan x Hulkling💚 on X: \"Danny DeVito y Joe Pesci rechazaron el papel de Iago. Finalmente el cómico Gilbert Gottfried fue quien le dió su voz y Danny daría la suya a Phil en Hercules años más tarde https://t.co/oarHZfEFLo\" / X",
      "link": "https://twitter.com/disneyfansontw1/status/1363894479825100800",
      "source": "X",
      "source_icon": "https://serpapi.com/searches/6777d9c3c3b5a0ac7f1a42bc/images/a010fa01d1356742bb4b23235244a6c457bac16f1bb318a131e937125502814b.png",
      "thumbnail": "https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcQZ_7u4RJS9XLT8AJW--iD67TeDmIs2ZSILFzvy-hleDueJZzNN",
      "thumbnail_width": 255,
      "thumbnail_height": 198,
      "image": "https://pbs.twimg.com/media/Eu2Gy8hXAAU_48Z.jpg",
      "image_width": 400,
      "image_height": 310
    },
  ],
  "related_content": [
    {
      "query": "Danny DeVito",
      "link": "https://lens.google.com/search?sca_esv=b9d59735341c7a85&hl=en&q=Danny+DeVito&kgmid=/m/0q9kd&sa=X&ved=2ahUKEwiKrva2yNmKAxUZTGwGHdTjAPQQ9_gLKAB6BQiJARAB",
      "thumbnail": "https://serpapi.com/searches/6777d9c3c3b5a0ac7f1a42bc/images/fbe7f81a6cec6c4671f9787e89ce797e072786289c7481dc36207997a4d6b5a0.jpeg",
      "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google&google_domain=google.com&hl=en&kgmid=%2Fm%2F0q9kd&q=Danny+DeVito"
    }
  ],
  "exact_matches_page_token": "TdWaIXicTY_LkppAGIVfKE4QHGB2-bmrNJcBEd1QXFpoEVEbUFlmn3fIaJKZmmSR1_FtYiqbnM2p8y2-qvP52y5uitePFMeHtPi1b_HhHO3iQ1zRL680jSNMu98My68ygY85nh2lnDh62X_93tEDyW6fZGeFd4-MpMJ4Ad64tHy3R3pQIh81tjIpLMIw1rocmv5mbfXQ2D4cl4pGllVQWWu3f88pppTU27uMN4Jzp0zKcRvmSlXoVLICixMWCSvI3iYPnTA9r3zEzuWIMwhAlTwG5yR_3_yn0LWkn3LY4gZMM7BR16H5yeZHfhnE9MlbolNjKsNYDJ0hQrxaauaTOjOP9zcZqd7E0fDDkGGY-yTb5qbLMN4rUMsypB7k-VQHNQe_XsvFwoJ7nNPsb0WGC5Ar4gZABqcHSUWlrtu5MfnH3zZbGlV1hi_t9get20OKf97RwxEnD225vbZZdRmJ11VCbyZIve1HMuMJAoXpkoeVaESa12vnnjHnPo6Rpi9mVqTTZJGEToX50GcLKkQ7kkwbvKSMxJU70fFa0l9o_BJeO5zdBmxczKbqkTyLCSeTxjPhNMOCWCpGwuvIrl3K5ybO3bF8AukP9XS-Zw",
  "serpapi_exact_matches_link": "https://serpapi.com/search.json?engine=google_lens&page_token=TdWaIXicTY_LkppAGIVfKE4QHGB2-bmrNJcBEd1QXFpoEVEbUFlmn3fIaJKZmmSR1_FtYiqbnM2p8y2-qvP52y5uitePFMeHtPi1b_HhHO3iQ1zRL680jSNMu98My68ygY85nh2lnDh62X_93tEDyW6fZGeFd4-MpMJ4Ad64tHy3R3pQIh81tjIpLMIw1rocmv5mbfXQ2D4cl4pGllVQWWu3f88pppTU27uMN4Jzp0zKcRvmSlXoVLICixMWCSvI3iYPnTA9r3zEzuWIMwhAlTwG5yR_3_yn0LWkn3LY4gZMM7BR16H5yeZHfhnE9MlbolNjKsNYDJ0hQrxaauaTOjOP9zcZqd7E0fDDkGGY-yTb5qbLMN4rUMsypB7k-VQHNQe_XsvFwoJ7nNPsb0WGC5Ar4gZABqcHSUWlrtu5MfnH3zZbGlV1hi_t9get20OKf97RwxEnD225vbZZdRmJ11VCbyZIve1HMuMJAoXpkoeVaESa12vnnjHnPo6Rpi9mVqTTZJGEToX50GcLKkQ7kkwbvKSMxJU70fFa0l9o_BJeO5zdBmxczKbqkTyLCSeTxjPhNMOCWCpGwuvIrl3K5ybO3bF8AukP9XS-Zw"
}
    
    gemini = Gemini("misleading_image/google.key")

    tweet_image = Image.open(BytesIO(requests.get(tweet_image).content))
    response = generate_community_note(tweet_text, tweet_image, ris_results, gemini, google_ground=False, dememe=False)
    print(response.text)

if __name__ == "__main__":
    main()