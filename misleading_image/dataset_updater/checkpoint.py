import os
import pickle
import json
import datetime


class Checkpoint:
    """
    A list of steps that led to the current state as well as a path to the dataset.

    :param dataset_path: Path to the dataset file (JSON)
    :param checkpoint: Existing Checkpoint object to copy from
    :param checkpoint_path: Path to a saved checkpoint file (pickle)
    """

    def __init__(self, dataset=None, dataset_path=None, checkpoint=None, checkpoint_path=None,
                 output_directory="./output"):
        self.output_directory = output_directory  # Default or user-defined output directory

        if checkpoint:
            self.executed_steps = checkpoint.executed_steps.copy()
            self.dataset = checkpoint.dataset.copy()
            self.dataset_path = checkpoint.dataset_path
            self.created_at = datetime.datetime.now()

        elif dataset_path:
            self.executed_steps = []
            self.dataset_path = dataset_path
            with open(dataset_path, "r") as f:
                self.dataset = json.load(f)
            self.created_at = datetime.datetime.now()

        elif checkpoint_path:
            with open(checkpoint_path, "rb") as f:
                checkpoint = pickle.load(f)
                self.executed_steps = checkpoint.executed_steps.copy()
                self.dataset = checkpoint.dataset.copy()
                self.dataset_path = checkpoint.dataset_path
                self.output_directory = checkpoint.output_directory  # Ensure output_directory persists when loading from pickle
                self.created_at = datetime.datetime.now()
        elif dataset is not None:
            self.executed_steps = []
            self.dataset = dataset
            self.dataset_path = None
            self.created_at = datetime.datetime.now()

        else:
            raise ValueError("Must provide either a dataset, dataset path, a checkpoint, or a checkpoint path")

        # Ensure the output directory exists
        os.makedirs(self.output_directory, exist_ok=True)

    def __str__(self):
        return "Checkpoint with steps: " + ", ".join([step.name for step in self.executed_steps])

    def save(self, file_name=None):
        """
        Save the checkpoint to a file.

        :param file_name: Name of the file to save the checkpoint to
        """
        if not file_name:
            file_name = f"checkpoint_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_"
            file_name += "-".join([step.name for step in self.executed_steps]) + ".pkl"
            file_path = os.path.join(self.output_directory, file_name)
        else:
            file_path = os.path.join(self.output_directory, file_name)

        with open(file_path, "wb") as f:
            pickle.dump(self, f)

        return file_path

    @staticmethod
    def load(file_path):
        """
        Load a checkpoint from a file.

        :param file_path: Path to the file from which the checkpoint will be loaded
        :return: Loaded Checkpoint object
        """
        with open(file_path, 'rb') as f:
            return pickle.load(f)

    def get_dataset(self):
        """
        Return the dataset. If dataset_path is provided, reload from file.

        :return: The dataset (loaded from memory or file)
        """
        if hasattr(self, 'dataset_path') and self.dataset_path:
            with open(self.dataset_path, "r") as f:
                self.dataset = json.load(f)
        return self.dataset

    def to_json(self, file_path):
        """
        Export the checkpoint metadata to a JSON file.

        :param file_path: Path to the JSON file for exporting metadata
        """
        metadata = {
            'timestamp': self.created_at.isoformat(),
            'executed_steps': [step.name for step in self.executed_steps],
            'dataset_path': getattr(self, 'dataset_path', None)
        }
        with open(file_path, 'w') as f:
            json.dump(metadata, f, indent=4)

    def mark_step_completed(self, step, name=None):
        """
        Record the completion of a step and save the checkpoint.

        :param name: Optional name for the checkpoint file
        :param step: Step instance that was executed
        """
        self.executed_steps.append(step)

        if name:
            checkpoint_file_path = self.save(name)
        else:
            checkpoint_file_path = self.save()

        return checkpoint_file_path

    def __repr__(self):
        return f"Checkpoint(created at {self.created_at}, steps: {[step.name for step in self.executed_steps]})"
