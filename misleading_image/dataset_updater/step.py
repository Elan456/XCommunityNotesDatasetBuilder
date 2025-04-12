import inspect
import logging
from typing import List, Callable

from misleading_image.dataset_updater.checkpoint import Checkpoint


class Step:
    def __init__(self, name: str, action: Callable, preconditions: List['Step'] = None, execution_args: List[str] = None):
        self.name = name
        self.preconditions = preconditions if preconditions else []
        self.action = action
        self.execution_args = execution_args if execution_args else []

    def execute(self, checkpoint: Checkpoint, output_name=None, **kwargs):
        logger = logging.getLogger(__name__)

        # Check if preconditions are met
        if all(step.name in [s.name for s in checkpoint.executed_steps] for step in self.preconditions):
            try:
                # Check if kwargs match the expected parameters
                # Check if kwargs match the expected parameters
                sig = inspect.signature(self.action)
                for param in sig.parameters.values():
                    if param.name == 'checkpoint':
                        continue
                    if param.name not in kwargs and param.default == inspect.Parameter.empty:
                        raise ValueError(f"Missing required argument: {param.name}")

                # Execute the action
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