import json

import httpx


class Rotator:

    def __init__(self, keys_file):
        self.keys = []
        with open(keys_file, 'r') as f:
            self.keys = json.load(f)
        self.current_key = 0

    def get_next_key(self):
        key_pair = self.keys[self.current_key]
        self.current_key = (self.current_key + 1) % len(self.keys)
        return key_pair['api_key'], key_pair['engine_id']


    def google_search(self, query, **params):
        api_key, engine_id = self.get_next_key()
        url = "https://www.googleapis.com/customsearch/v1"
        params.update({
            "key": api_key,
            "cx": engine_id,
            "q": query,
            **params
        })
        response = httpx.get(url, params=params)
        response.raise_for_status()
        return response.json()