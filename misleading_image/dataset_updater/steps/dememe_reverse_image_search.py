import json
from io import BytesIO

from PIL import Image
import requests

from misleading_image.dataset_updater.checkpoint import Checkpoint
from misleading_image.dataset_updater.step import Step
from misleading_image.dememe import remove_meme_text


def dememe_reverse_image_search(checkpoint, dataset_json=None, rvrse_checkpoint=None):
    """
    Perform reverse image search on the dataset images, with dememeing

    :param rvrse_checkpoint:  Checkpoint containing reverse image search results, if a checkpoint is not provided.
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

    # Load normal reverse image search results if provided
    normal_reverse_image_search_results = {}
    if rvrse_checkpoint:
        normal_reverse_image_search_results = {
            result['tweetId']: {
                "response": result['response']
            }
            for result in Checkpoint.load(rvrse_checkpoint).get_dataset()
        }

    dememeReverseImageSearchResults = []

    # For each tweet, need to send img URL to API and get a response
    # Store tweetId, imgURL, and API response in a list
    for tweet in current_dataset:
        tweetId = tweet['id']
        imgURL = tweet['image_urls'][0]

        # Convert image to PIL image
        response = requests.get(imgURL)
        my_img = Image.open(BytesIO(response.content))

        # Dememe the image
        cleaned_image, cropped_text = remove_meme_text(my_img)

        print(cropped_text)

        # If the image was not cropped, use the normal reverse image search result if available
        if not cropped_text and tweetId in normal_reverse_image_search_results:
            tweet['dememe_image_search_results'] = {"response": normal_reverse_image_search_results[tweetId]['response'], "removedText": None}
        else:
            # Host image temporarily and send hostedImage URL to API and get response
            # Store response in reverseImageSearchResults
            response = [
                {
                    "position": 1,
                    "title": "The New Obama Administration Defense Of Police Militarization: The Boston Bombing",
                    "link": "https://www.buzzfeednews.com/article/evanmcsan/the-boston-defense",
                    "source": "BuzzFeed News",
                    "source_icon": "https://serpapi.com/searches/67b8c688c24d6096bd5718f2/images/fa4176daf8c26db1febd592788b976b52782c6eaee8a4c5a493513438827a106.png",
                    "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSGwd_HIFBTsVS8mXIbuiEcXswNFYTl9YtS13YwIlXPqc3Ei6R_",
                    "thumbnail_width": 183,
                    "thumbnail_height": 275,
                    "image": "https://img.buzzfeed.com/buzzfeed-static/static/2014-12/7/23/campaign_images/webdr04/the-new-obama-administration-defense-of-police-mi-2-16197-1418012533-5_big.jpg",
                    "image_width": 236,
                    "image_height": 355
                },
            ]
            tweet['dememe_image_search_results'] = {"response": response, "removedText": cropped_text}
            # dememeReverseImageSearchResults.append({"tweetId": tweetId, "removedText": cropped_text, "response": response})

    # Save reverse image results as a new checkpoint
    checkpoint.dataset = current_dataset

dememe_reverse_image_search_step = Step(name="Dememe Reverse Image Search", action=dememe_reverse_image_search, execution_args=['dataset_json', 'checkpoint', 'rvrse_checkpoint'], )
