import json
import os

from serpapi import GoogleSearch
from google.cloud import vision

from misleading_image.dataset_updater.step import Step

#define a search using serp and a search using google vision
def search_with_serpapi(current_dataset):
    with open("misleading_image/dataset_updater/serp.key", 'r') as f:
        serp_key = f.read().strip()
    for tweet in current_dataset:
        imgURL = tweet['image_urls'][0]
        # send imgURL to API and get response
        # store response in reverseImageSearchResults
        params = {
            "engine": "google_lens",
            "url": imgURL,
            "api_key": serp_key,
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        try:
            visual_matches = results["visual_matches"][:16]
            if visual_matches:
                tweet['reverse_image_search_results'] = visual_matches
        except KeyError:
            tweet['reverse_image_search_results'] = []

def search_with_google_vision(currentDataset):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'misleading_image/dataset_updater/google_cloud/client_file_googlevision.json'
    client = vision.ImageAnnotatorClient()
    image = vision.Image()

    for tweet in currentDataset:
        image.source.image_uri = tweet['image_urls'][0]
        # Send imgURL to API and get response
        try:
            response = client.web_detection(image=image)
            annotations = response.web_detection

            reverse_image_search_results = []

            if annotations.pages_with_matching_images:
                for page in annotations.pages_with_matching_images:
                    page_info = {
                        "page_url": page.url,
                        "title": page.page_title,
                        "full_matching_images": [image.url for image in page.full_matching_images],
                        "partial_matching_images": [image.url for image in page.partial_matching_images]
                    }
                    reverse_image_search_results.append(page_info)

            tweet['reverse_image_search_results'] = reverse_image_search_results
        except Exception as e:
            tweet['reverse_image_search_results'] = []

def reverse_image_search(checkpoint, dataset_json=None, search_method='google_vision'):
    """
    Perform reverse image search on the dataset images, without dememeing

    :param checkpoint: The Checkpoint object to update.
    :param dataset_json: Path to the JSON file representing the dataset, if a checkpoint is not provided.
    :param search_method: The method to use for reverse image search, either 'google_vision' or 'serpapi'.
    """

    # Check if the step has already
    if any(step.name == "Reverse Image Search" for step in checkpoint.executed_steps):
        print("Skipping step as it has already been executed")
        return

    # Load the dataset from the checkpoint or JSON file
    if dataset_json:
        with open(dataset_json, 'r') as f:
            current_dataset = json.load(f)
    else:
        current_dataset = checkpoint.dataset
    # view if the search method is serp or google vision
    if search_method == 'google_vision':
        search_with_google_vision(current_dataset)
    elif search_method == 'serpapi':
        # Load the serpapi key from the file
        search_with_serpapi(current_dataset)
    checkpoint.dataset = current_dataset

reverse_image_search_step = Step(name="Reverse Image Search", action=reverse_image_search, execution_args=['dataset_json', 'checkpoint'], )