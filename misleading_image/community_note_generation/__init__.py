
import json 
import pandas as pd 
import random 
import requests
import re

def clean_text(text):
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Replace newlines, tabs, and commas with spaces
    text = text.replace('\n', '&newline').replace('\t', '&tab').replace(',', '&comma').replace('\"', '&quote')
    return text

def get_test_set(dataset_path: str, size=10) -> pd.DataFrame:
    """
    Load the dataset and return a DataFrame with columns 'text', 'image_urls', 'community_note'.
    """
    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    # Create a DataFrame
    df = pd.DataFrame(dataset)

    # Filter out rows with no image_urls i.e. len(image_urls) == 0
    df = df[df["image_urls"].apply(lambda x: len(x) > 0)]

    # Sample down to 50
    random.seed(0)
    df = df.sample(int(size*1.2))

    # Filter out rows where the image_url is broken
    # i.e. the image_url returns a 404
    def check_image_url(url):
        try:
            response = requests.get(url)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(e)
            return False
        

    print("Checking image urls...")
    df = df[df["image_urls"].apply(lambda x: all(check_image_url(url) for url in x))]
    print("Found {} good tweets".format(len(df)))

    # Chose 15 random rows
    random.seed(0)
    df = df.sample(size)

    # Clean the tweet text
    df["text"] = df["text"].apply(lambda x: clean_text(x))

    # Take the text, image_urls, and community_note["summary"] as columns
    generation_df = df[["id", "text", "image_urls", "tweet_url", "reverse_image_search_results", "dememe_reverse_image_search_results"]].copy()
    generation_df["original_cn"] = df["community_note"].apply(lambda x: x["summary"])

    return generation_df