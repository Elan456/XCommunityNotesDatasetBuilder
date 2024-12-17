import google.generativeai as genai
from .twc import TweetWithContext
from typing import List
import os 
import json 
import PIL.Image as Image
from tqdm import tqdm
import time 

class Gemini:
    def __init__(self, keys_file):
        self.keys = [key.strip() for key in open(keys_file, "r").readlines()]
        self.current_key_index = 0

    def get_max_rpm(self):
        return len(self.keys) * 14
    
    def generate(self, prompt):
        genai.configure(api_key=self.keys[self.current_key_index])
        self.current_key_index = (self.current_key_index + 1) % len(self.keys)

        self.model = genai.GenerativeModel("gemini-1.5-flash")
        done = False 
        while not done: 
            try:
                response = self.model.generate_content(prompt)
                done = True
            except Exception as e:
                print("Exception when generating content: ", e)
                print("Sleeping, and switching to next key")
                genai.configure(api_key=self.keys[self.current_key_index])
                self.current_key_index = (self.current_key_index + 1) % len(self.keys)
                time.sleep(10)
        return response
    
gemini = Gemini("misleading_image/google.key")  # Initialize the gemini model

def gemini_filter_misleading_images(tweets: List[TweetWithContext]):
    """
    Uses Gemini to add a classification to each tweet's image as either "contextual" or "misleading"
    Returns the same list of tweets with the added classification to each object
    """
    # Pre load and rewrite the json file without any non-ascii characters
    # pj = json.load(open("misleading_image/prompts/p1.json", "r", encoding="utf-8"))
    # with open("misleading_image/prompts/p1.json", "w") as f:
    #     json.dump(pj, f, ensure_ascii=True, indent=4)

    start_time = time.time()
    requests_made = 0


    prompt_base_json = json.load(open("misleading_image/prompts/p1.json", "r"))

    prompt_base = ["A contextual image is an image that isn't intended to mislead, but can be taken out of context if the tweet text doesn't provide enough information. A misleading image is an image that is intended to mislead the viewer on it's own regardless of the tweet text. Please determine if the image is contextual or misleading based on the tweet text and image."]
    prompt_base.append("Below are a few examples")
    for item in prompt_base_json["entries"]:
        for key, value in item.items():
            if key != "img_path":
                if key == "classification":
                    key = "Image Classification"
                prompt_base.append(f"{key}: {value}")
            else:
                img_path = value
                img = Image.open(img_path)
                prompt_base.append(img)
    iterator = tqdm(tweets)
    iterator.set_description("Classifying images")
    for tweet in iterator:
        rpm = requests_made / (time.time() - start_time) / 60
        if rpm > gemini.get_max_rpm():
            print("Current RPM is ", rpm, " sleeping for 10 seconds")
            time.sleep(10)

        prompt = prompt_base.copy()
        prompt.append("Is the image itself a contextual image or misleading image? If the image itself isn't misleading but is being used incorrectly, then it is a contextual image. If the image is misleading on its own, then it is a misleading image.")
        prompt.append(f"Tweet: {tweet.text}")
        prompt.append(f"Community Note: {tweet.community_note}")
        prompt.append(tweet.image)
        prompt.append("""Respond in the format: {"classification": "contextual"} or {"classification": "misleading"}. Followed by your resoning for the classification.""")
        response = gemini.generate(prompt)
        requests_made += 1

        # Check if the response says misleading or contextual

        r_text = response.text.lower()
        m_loc = r_text.find("misleading")
        c_loc = r_text.find("contextual")

        if m_loc != -1 and c_loc != -1:
            classification = "misleading" if m_loc < c_loc else "contextual"
        elif m_loc != -1 and c_loc == -1:
            classification = "misleading"
        elif c_loc != -1 and m_loc == -1:
            classification = "contextual"
        else:
            classification = "unknown"

        # print(response)
        # print("Parsed classification: ", classification)
        tweet.llm_image_classification = classification
        tweet.full_llm_image_response = response.text

    return tweets

if __name__ == "__main__": # Quick test
    tweet_misleading = TweetWithContext("Sex offending rate of women: 3 per one million Sex offending rate of men: 395 per million Sex offending rates of transwomen: 1,916 per million",
                            "misleading_image/imgs/sex_offending.jpg", 
                            "The UK government estimates there are between 250,000 and 500,000 trans individuals in the UK.    https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/721642/GEO-LGBT-factsheet.pdf#:~:text=We%20tentatively%20estimate%20that%20there%20are%20approximately%20200%2C000-500%2C000,whether%20and%20how%20to%20develop%20a%20population%20estimate.    This image overstates the rate of such offenses by severely undercounting the trans population. The actual rate using that figure is 5-10x lower, below cisgender men.")
    
    tweet_contextual = TweetWithContext("Jaffa Tel Aviv is not safe.","misleading_image/imgs/moscow_fire.jpg",
                                        "The image is from a gas explosion which happened in Moscow in April 2009.  https://ria.ru/20090510/170619872.html")
    
    gemini_filter_misleading_images([tweet_misleading, tweet_contextual])
