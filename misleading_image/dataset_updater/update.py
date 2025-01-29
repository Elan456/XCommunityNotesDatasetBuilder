from step import Step, Checkpoint

def update(checkpoint: Checkpoint, step: Step):
    """
    Update the dataset with the given step
    """
    step.execute(checkpoint)
    print(f"Executed step {step.name}")