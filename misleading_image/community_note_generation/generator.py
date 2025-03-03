
from misleading_image.twc import TweetWithContext as TWC
from tqdm import tqdm 

import re

def clean_text(text):
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Replace newlines, tabs, and commas with spaces
    text = text.replace('\n', ' ').replace('\t', ' ').replace(',', ' ')
    return text


def generate(df, func, name, gemini, **kwargs):

    print("genearating", name)
    
    # If this column is already in the dataframe, return the dataframe
    if name in df.columns:
        print("Skipping generation of", name)
        return df
    
    outs = [] 
    for index, row in tqdm(df.iterrows()):
        tweet = TWC(row["text"], row['image_urls'][0], row['original_cn'])
        if "ris" in name:
            response = func(tweet.text, tweet.image, row["reverse_image_search_results"], gemini, **kwargs)
        else:
            response = func(tweet.text, tweet.image, gemini, **kwargs)
        response_text = clean_text(response.text)
        outs.append(response_text)
    df[name] = outs
    return df