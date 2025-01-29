from typing import List
import pickle
import datetime
import json
import logging


class Step:
    """
    Any action tht can be taken on a dataset
    Can have preconditions and postconditions

    :param name: The name of the step
    :param preconditions: A list of steps that must be executed
    :param action: The action to take (function)
    :param execution_args: A list of arguments that must be passed to the action during execution
    """
    def __init__(self, name, preconditions: List["Step"], action, execution_args=[]):
        self.name = name 
        self.preconditions = preconditions
        self.action = action

    def execute(self, checkpoint, kwargs=None):
        for arg in self.execution_args:
            if arg not in kwargs:
                raise ValueError(f"Missing argument {arg} in execution of step {self.name}")

        logger = logging.getLogger(__name__)
        try:
            if all(step in checkpoint.executed_steps for step in self.preconditions):
                self.action(checkpoint, kwargs)
                if self not in checkpoint.executed_steps:
                    checkpoint.executed_steps.append(self)
                logger.info(f"Executed step: {self.name}")
            else:
                unmet = [step.name for step in self.preconditions if step not in checkpoint.executed_steps]
                logger.warning(f"Preconditions not met for step {self.name}: {unmet}")
        except Exception as e:
            logger.error(f"Failed to execute step {self.name}: {e}")
            raise
