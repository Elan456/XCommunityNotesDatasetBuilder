import json
from misleading_image.dataset_updater.step import Step

def are_schemas_compatible(dataset1, dataset2):
    """
    Check if two datasets have compatible schemas.
    :param dataset1: First dataset to compare.
    :param dataset2: Second dataset to compare.
    :return: True if schemas are compatible, False otherwise.
    """
    keys1 = set(dataset1[0].keys())
    keys2 = set(dataset2[0].keys())
    
    # Check if the keys of both datasets match
    return keys1 == keys2

def combine_datasets(checkpoint, current_checkpoint=None, current_dataset=None, check_steps=True):
    """
    Combine two datasets into one, ideally joining novel data to an existing dataset.
    :param checkpoint: The Checkpoint object to update.
    :param current_dataset: Path to the current dataset JSON file.
    :param current_checkpoint: The current Checkpoint object.
    """
    
    # Load the current dataset
    if current_dataset is None:
        current_dataset = current_checkpoint.dataset
    else:
        with open(current_dataset, 'r') as f:
            current_dataset = json.load(f)

    # Check if the schemas are compatible
    if not are_schemas_compatible(checkpoint.dataset, current_dataset):
        raise ValueError("The schemas of the two datasets are not compatible.")
    
    if check_steps:
        # Check if the steps are compatible
        for step in checkpoint.executed_steps:
            if step not in current_checkpoint.executed_steps:
                raise ValueError(f"Step {step} is not compatible with the current checkpoint, as it was not executed in the current dataset.")

    # Combine the datasets
    combined_dataset = checkpoint.dataset + current_dataset

    # Update the checkpoint with the combined dataset
    checkpoint.dataset = combined_dataset


combine_datasets_step = Step(
    name="Combine Datasets",
    action=combine_datasets,
    execution_args=['checkpoint', 'current_checkpoint'],
)

