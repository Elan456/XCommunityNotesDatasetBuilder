import json 
import pickle 
import datetime

class Checkpoint:
    """
    A list of steps that led to the current state as well as a path to the dataset
    """
    def __init__(self, dataset_path=None, checkpoint=None, checkpoint_path=None):
        if checkpoint:
            self.executed_steps = checkpoint.executed_steps.copy()
            self.dataset = checkpoint.dataset.copy()

        elif dataset_path:
            self.executed_steps = []
            with open(dataset_path, "r") as f:
                self.dataset = json.load(f)

        elif checkpoint_path:
            with open(checkpoint_path, "rb") as f:
                checkpoint = pickle.load(f)
                self.executed_steps = checkpoint.executed_steps.copy()
                self.dataset = checkpoint.dataset.copy()

        else:
            raise ValueError("Must provide either a dataset path or a checkpoint")


    def __str__(self):
        return "Checkpoint with steps: " + ", ".join([step.name for step in self.executed_steps])

    def save(self):
        """
        Save the checkpoint to a file
        """

        # File name with data and steps
        file_name = f"checkpoint_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_"
        file_name += "-".join([step.name for step in self.executed_steps]) + ".pkl"
        with open(file_name, "wb") as f:
            pickle.dump(self, f)
