from misleading_image.add_topical_category import main as add_topical_category
from misleading_image.dataset_updater.step import Step

def add_topical_categories(checkpoint):
    """
    Adds topical categories to the images in the dataset

    run as python -m misleading_image.dataset_updater.update --checkpoint_path="" --step_name="Add Topical Categories"
    """
    

    if any(step.name== "Add Topical Categories" for step in checkpoint.executed_steps):
        print("Existing step already executed")
        return
    
    existing_dataset = checkpoint.dataset
    dataset_topical_categories = add_topical_category(existing_dataset, return_output=True)
    dataset_topical_categories = [tweet for tweet in dataset_topical_categories if 'topical_categories' in tweet]
    checkpoint.dataset = dataset_topical_categories

add_topical_categories_step = Step(name="Add Topical Categories", action=add_topical_categories)
