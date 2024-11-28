import google.generativeai as genai
from .twc import TweetWithContext
from typing import List
import os 
import json 
import PIL.Image as Image

class Gemini:
    def __init__(self):
        genai.configure(api_key=open("misleading_image/google.key", "r").read())
        self.model = genai.GenerativeModel("gemini-1.5-flash")
    
    def generate(self, prompt):
        response = self.model.generate_content(prompt)
        return response
    
gemini = Gemini()

def gemini_filter_misleading_images(tweets: List[TweetWithContext]):
    prompt_base = json.load("misleading_image/prompts/p1.json")

    for tweet in tweets:
        prompt = prompt_base.copy()
        prompt["input"]["text"] = tweet.text
        prompt["input"]["image"] = tweet.image_path
        prompt["input"]["community_note"] = tweet.community_note

        response = gemini.generate(prompt)
        tweet.image_path = response["output"]["image"]
        tweet.text = response["output"]["text"]
        tweet.community_note = response["output"]["community_note"]
