import json
import time

import httpx


class Rotator:

    def __init__(self, keys_file):
        self.keys = []
        with open(keys_file, 'r') as f:
            self.keys = json.load(f)
        self.current_key = 0
        self.requests_made = {i: 0 for i in range(len(self.keys))}
        self.start_time = time.time()


    def get_next_key(self):
        while True:
            key_pair = self.keys[self.current_key]
            api_key = key_pair['api_key']
            if self.requests_made[self.current_key] < 95:
                self.current_key = (self.current_key + 1) % len(self.keys)
                return api_key, key_pair['engine_id']
            else:
                elapsed_time = time.time() - self.start_time
                if elapsed_time < 60:
                    sleep_time = 65 - elapsed_time
                    print(f"Rate limit reached for key {self.current_key}. Sleeping for {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    self.requests_made[self.current_key] = 0
                    self.start_time = time.time()

    def google_search(self, query, **params):
        api_key, engine_id = self.get_next_key()
        url = "https://www.googleapis.com/customsearch/v1"
        params.update({
            "key": api_key,
            "cx": engine_id,
            "q": query,
            **params
        })
        try:
            response = httpx.get(url, params=params)
            response.raise_for_status()
            self.requests_made[self.current_key] += 1  # Update the requests_made dictionary here
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            return None
        return response.json()