import json
from misleading_image.dataset_updater.google_cloud.rotator import Rotator

from misleading_image.dataset_updater.step import Step

NUMBER_IMAGES_TO_SEARCH = 3
NUMBER_IMAGE_CONTEXTS = 3

def image_link_annotation(checkpoint, dataset_json=None):
    """
    use the google search api to collect the titles and snippets of links associated with images in the dataset
    :param checkpoint: the checkpoint object to update
    :param dataset_json: Path to the JSON file representing the dataset for use if a checkpoint is not provided.
    """

    if any(step.name == "Image Link Annotation" for step in checkpoint.executed_steps):
        print("Skipping step as it has already been executed")
        return
    # see if either dememe reverse image or reverse image search has been executed

    # elif not any(step.name == "Dememe Reverse Image" for step in checkpoint.executed_steps):
    #     print("Skipping step as it requires the Dememe Reverse Image step to be executed first")
    #     return
    #
    # elif not any(step.name == "Reverse Image Search" for step in checkpoint.executed_steps):
    #     print("Skipping step as it requires the Reverse Image Search step to be executed first")
    #     return



    if dataset_json:
        with open(dataset_json, 'r') as f:
            current_dataset = json.load(f)
    else:
        current_dataset = checkpoint.dataset

    rotator = Rotator('misleading_image/dataset_updater/google_cloud/google_cloud.key')
    for tweet in current_dataset:
        reverse_image_search_results = tweet.get('reverse_image_search_results', [])
        for ris_result_num in range(min(NUMBER_IMAGES_TO_SEARCH, len(reverse_image_search_results))):
            ris_result = reverse_image_search_results[ris_result_num]
            try:
                page_url = ris_result.get('page_url')
                if not page_url:
                    continue

                response = rotator.google_search(page_url)
                search_results = response.get('items', [])[:NUMBER_IMAGE_CONTEXTS]

                if 'image_context' not in ris_result:
                    ris_result['image_context'] = []

                for search_result in search_results:
                    context = {
                        'title': search_result.get('title'),
                        'link': search_result.get('link'),
                        'snippet': search_result.get('snippet')
                    }
                    ris_result['image_context'].append(context)
            except Exception as e:
                print(f"Error processing tweet: {e}")

    checkpoint.dataset = current_dataset


image_link_annotation_step = Step(name="Image Link Annotation", action=image_link_annotation,
                                  execution_args=['dataset_json', 'checkpoint'])