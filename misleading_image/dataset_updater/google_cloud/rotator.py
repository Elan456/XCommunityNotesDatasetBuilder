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
        self.start_times = {i: time.time() for i in range(len(self.keys))}


    def get_next_key(self):
        for _ in range(len(self.keys)):
            key_index = self.current_key
            if self.requests_made[key_index] < 95:
                key_pair = self.keys[key_index]
                return key_pair['api_key'], key_pair['engine_id'], key_index
            self.current_key = (self.current_key + 1) % len(self.keys)

        # All keys are rate-limited → wait
        key_index = self.current_key
        elapsed_time = time.time() - self.start_times[key_index]
        if elapsed_time < 59:
            sleep_time = 61 - elapsed_time  # Give a 1-second buffer
            print(f"All keys exhausted. Sleeping for {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)

        self.requests_made[key_index] = 0
        self.start_times[key_index] = time.time()

        key_pair = self.keys[key_index]
        return key_pair['api_key'], key_pair['engine_id'], key_index

    def google_search(self, query, **params):
        api_key, engine_id, key_index = self.get_next_key()
        url = "https://www.googleapis.com/customsearch/v1"
        params.update({
            "key": api_key,
            "cx": engine_id,
            "q": query,
            **params
        })

        while True:
            try:
                response = httpx.get(url, params=params)
                response.raise_for_status()
                self.requests_made[key_index] += 1
                self.current_key = (key_index + 1) % len(self.keys)
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    print(f"Rate limit exceeded for key {key_index}. Sleeping for 60 seconds...")
                    time.sleep(60)
                    self.requests_made[key_index] = 0
                    self.start_times[key_index] = time.time()
                else:
                    print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                    return None
            except Exception as e:
                print(f"Unexpected error occurred: {e}")
                return None
