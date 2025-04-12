import argparse
import json

from misleading_image.dataset_updater.checkpoint import Checkpoint
from .step import Step

from .steps.add_image_labels import add_image_labels_step
from .steps.filter_community_notes import filter_community_notes_step
from .steps.reverse_image_search import reverse_image_search_step
from .steps.dememe_reverse_image_search import dememe_reverse_image_search_step
from .steps.remove_existing_notes import remove_existing_notes_step
from .steps.collect_tweets import collect_tweets_step
from .steps.add_topical_categories import add_topical_categories_step
from .steps.combine_datasets import combine_datasets_step
from .steps.image_annotation import image_link_annotation_step
from .steps.add_note_author_information import add_note_author_information_step
from .steps.add_note_status import add_note_status_step


def initialize(output_path="./output", checkpoint_name=None) -> str:
    """
    Initialize a checkpoint with an empty dataset and save it in output path to begin working.

    :param checkpoint_name: Name of the checkpoint file.
    :param output_path: Path to save the checkpoint file.
    :return: Path to the saved checkpoint file.
    """
    # Initialize a checkpoint with an empty dataset
    checkpoint = Checkpoint(dataset={}, output_directory=output_path)
    checkpoint_file_path = checkpoint.save(checkpoint_name)

    return checkpoint_file_path


valid_steps = [
    filter_community_notes_step,
    remove_existing_notes_step,
    reverse_image_search_step,
    dememe_reverse_image_search_step,
    image_link_annotation_step,
    collect_tweets_step,
    add_image_labels_step,
    add_topical_categories_step,
    combine_datasets_step,
    add_note_author_information_step,
    add_note_status_step,
]


def update(checkpoint: Checkpoint, step: Step):
    """
    Update the dataset with the given step
    """
    step.execute(checkpoint)
    print(f"Executed step {step.name}")


def main():
    parser = argparse.ArgumentParser(description="Apply a step to a checkpoint.")
    parser.add_argument("--checkpoint_path", help="Path to the checkpoint file.")
    parser.add_argument("--step_name", required=True, help="Name of the step to apply.")
    parser.add_argument("--kwargs", type=json.loads, default="{}",
                        help="JSON string of keyword arguments for the step.")
    parser.add_argument("--output_path", default="./output",
                        help="Path to save the checkpoint file if initializing.")
    parser.add_argument("--checkpoint_name", help="Name of the checkpoint file if initializing.")
    args = parser.parse_args()

    if args.step_name == "initialize":
        checkpoint_file_path = initialize(output_path=args.output_path, checkpoint_name=args.checkpoint_name)
        print(f"Initialized checkpoint saved at: {checkpoint_file_path}")
        return

    if not args.checkpoint_path:
        raise ValueError("checkpoint_path is required for steps other than 'initialize'.")

    # Load the checkpoint
    checkpoint = Checkpoint.load(args.checkpoint_path)

    # Find the step by name
    step = next((s for s in valid_steps if s.name == args.step_name), None)
    if not step:
        raise ValueError(f"Step '{args.step_name}' not found in valid steps.")

    # Execute the step with the provided keyword arguments
    step.execute(checkpoint, args.checkpoint_name, **args.kwargs)

if __name__ == "__main__":
    main()
