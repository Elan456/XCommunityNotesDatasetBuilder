from step import Step
from checkpoint import Checkpoint

valid_steps = [

]

def update(checkpoint: Checkpoint, step: Step):
    """
    Update the dataset with the given step
    """
    step.execute(checkpoint)
    print(f"Executed step {step.name}")