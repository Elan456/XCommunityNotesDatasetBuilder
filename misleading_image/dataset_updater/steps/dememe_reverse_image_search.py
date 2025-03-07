import json
import os
from io import BytesIO

from PIL import Image
import requests
from google.cloud import vision

from misleading_image.dataset_updater.checkpoint import Checkpoint
from misleading_image.dataset_updater.step import Step
from misleading_image.dememe import remove_meme_text


def pil_image_to_vision_image(pil_image):
    buffer = BytesIO()
    pil_image.save(buffer, format="PNG")
    content = buffer.getvalue()
    return vision.Image(content=content)

def search_with_google_vision_dememe(currentDataset, num_pages=3):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'misleading_image/dataset_updater/google_cloud/client_file_googlevision.json'
    client = vision.ImageAnnotatorClient()

    for tweet in currentDataset:
        imgURL = tweet['image_urls'][0]

        try:
            response = requests.get(imgURL)
            my_img = Image.open(BytesIO(response.content))
        except Exception as e:
            tweet['dememe_reverse_image_search_results'] = []
            tweet['dememe_reverse_image_text'] = None

        cleaned_image, cropped_text = remove_meme_text(my_img)

        if not cropped_text:
            #first check if 'reverse_image_search_results' exists in the tweet
            if 'reverse_image_search_results' in tweet:
                tweet['dememe_reverse_image_search_results'] = tweet['reverse_image_search_results']
                tweet['dememe_reverse_image_text'] = None
                continue

        image = pil_image_to_vision_image(cleaned_image)

        # Send imgURL to API and get response
        try:
            response = client.web_detection(image=image)
            annotations = response.web_detection

            reverse_image_search_results = []

            if annotations.pages_with_matching_images:
                for page in annotations.pages_with_matching_images[:num_pages]:
                    page_info = {
                        "page_url": page.url,
                        "title": page.page_title,
                        "full_matching_images": [image.url for image in page.full_matching_images],
                        "partial_matching_images": [image.url for image in page.partial_matching_images]
                    }
                    reverse_image_search_results.append(page_info)

            tweet['dememe_reverse_image_search_results'] = reverse_image_search_results
            tweet['dememe_reverse_image_text'] = cropped_text if cropped_text else None
        except Exception as e:
                tweet['dememe_reverse_image_search_results'] = []
                tweet['dememe_reverse_image_text'] = None

def dememe_reverse_image_search(checkpoint, dataset_json=None):
    """
    Perform reverse image search on the dataset images, with dememeing

    :param checkpoint: The Checkpoint object to update.
    :param dataset_json: Path to the JSON file representing the dataset, if a checkpoint is not provided.
    """

    # Check if the step has already been executed
    if any(step.name == "Dememe Reverse Image Search" for step in checkpoint.executed_steps):
        print("Skipping step as it has already been executed")
        return

    # Load the dataset from the checkpoint or JSON file
    if dataset_json:
        with open(dataset_json, 'r') as f:
            current_dataset = json.load(f)
    else:
        current_dataset = checkpoint.dataset

    search_with_google_vision_dememe(current_dataset)
    # Save reverse image results as a new checkpoint
    checkpoint.dataset = current_dataset

dememe_reverse_image_search_step = Step(name="Dememe Reverse Image Search", action=dememe_reverse_image_search, execution_args=['dataset_json', 'checkpoint'], )
