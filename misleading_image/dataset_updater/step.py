from typing import List, Callable
import logging


class Step:
    """
    Represents an action to be taken on a dataset. Each step can have preconditions (other steps that must
    be completed before this one) and can execute an associated action.

    :param name: The name of the step.
    :param preconditions: A list of Step instances that must be executed before this step.
    :param action: The function to execute when this step is run.
    :param execution_args: List of argument names required by the action function.
    """

    def __init__(self, name: str, action: Callable, preconditions: List['Step'] = None,
                 execution_args: List[str] = None):
        self.name = name
        self.preconditions = preconditions if preconditions else []
        self.action = action
        self.execution_args = execution_args if execution_args else []

    def execute(self, checkpoint, output_name=None, **kwargs):
        """
        Executes the step if all preconditions are met.

        :param output_name: name of checkpoint output
        :param checkpoint: The Checkpoint object to apply the action to.
        :param kwargs: Arguments required by the action.
        """
        logger = logging.getLogger(__name__)

        # Check if preconditions are met
        if all(step in checkpoint.executed_steps for step in self.preconditions):

            try:
                # Execute the action
                # import inspect and
                self.action(checkpoint, **kwargs)

                # Log the step execution
                if self not in checkpoint.executed_steps:
                    if output_name:
                        checkpoint_file_path = checkpoint.mark_step_completed(self, output_name)
                    else:
                        checkpoint_file_path = checkpoint.mark_step_completed(self)
                    logger.info(f"Executed step: {self.name}")
                    return checkpoint_file_path
                else:
                    logger.info(f"Step '{self.name}' already executed")



            except Exception as e:
                logger.error(f"Failed to execute step '{self.name}': {e}")
                raise

        else:
            unmet = [step.name for step in self.preconditions if step not in checkpoint.executed_steps]
            logger.warning(f"Preconditions not met for step '{self.name}': {unmet}")

    def __repr__(self):
        return f"Step(name={self.name})"