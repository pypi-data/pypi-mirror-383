from enum import Enum
from typing import List, Tuple

import numpy as np
from pydantic.v1 import BaseModel, conint, conlist

__all__ = ["QuEraTaskResults", "TaskProbabilities"]

# TODO: add version to these models.


class QuEraShotStatusCode(str, Enum):
    Completed = "Completed"
    MissingPreSequence = "MissingPreSequence"
    MissingPostSequence = "MissingPostSequence"
    MissingMeasurement = "MissingMeasurement"


class QuEraTaskStatusCode(str, Enum):
    """
    An Enum representing the various states a task can be in within the QuEra system.

    Attributes:
        Created: The task has been created but not yet started.
        Running: The task is currently running.
        Completed: The task has completed successfully.
        Failed: The task has failed.
        Cancelled: The task has been cancelled.
        Executing: The task is currently being executed.
        Enqueued: The task is in the queue waiting to be executed.
        Accepted: The task has been accepted for execution.
        Unaccepted: The task has not been accepted for execution.
        Partial: The task has partially completed.
        Unsubmitted: The task has not been submitted for execution.
    """

    Created = "Created"
    Running = "Running"
    Completed = "Completed"
    Failed = "Failed"
    Cancelled = "Cancelled"
    Executing = "Executing"
    Enqueued = "Enqueued"
    Accepted = "Accepted"
    Unaccepted = "Unaccepted"
    Partial = "Partial"
    Unsubmitted = "Unsubmitted"


class QuEraShotResult(BaseModel):
    shot_status: QuEraShotStatusCode = QuEraShotStatusCode.MissingMeasurement
    pre_sequence: conlist(conint(ge=0, le=1), min_items=0) = []
    post_sequence: conlist(conint(ge=0, le=1), min_items=0) = []


class TaskProbabilities(BaseModel):
    probabilities: List[Tuple[Tuple[str, str], float]]

    def simulate_task_results(self, shots=1) -> "QuEraTaskResults":
        bit_strings, probabilities = zip(*self.probabilities)

        indices = np.random.choice(len(probabilities), p=probabilities, size=shots)
        shot_outputs = []
        for index in indices:
            pre_string, post_string = bit_strings[index]
            pre_sequence = [int(bit) for bit in pre_string]
            post_sequence = [int(bit) for bit in post_string]

            shot_outputs.append(
                QuEraShotResult(
                    shot_status=QuEraShotStatusCode.Completed,
                    pre_sequence=pre_sequence,
                    post_sequence=post_sequence,
                )
            )

        return QuEraTaskResults(
            task_status=QuEraTaskStatusCode.Completed, shot_outputs=shot_outputs
        )


class QuEraTaskResults(BaseModel):
    task_status: QuEraTaskStatusCode = QuEraTaskStatusCode.Failed
    shot_outputs: conlist(QuEraShotResult, min_items=0) = []

    def export_as_probabilities(self) -> TaskProbabilities:
        """converts from shot results to probabilities

        Returns:
            TaskProbabilities: The task results as probabilties
        """
        counts = dict()
        nshots = len(self.shot_outputs)
        for shot_result in self.shot_outputs:
            pre_sequence_str = "".join(str(bit) for bit in shot_result.pre_sequence)

            post_sequence_str = "".join(str(bit) for bit in shot_result.post_sequence)

            configuration = (pre_sequence_str, post_sequence_str)
            # iterative average
            current_count = counts.get(configuration, 0)
            counts[configuration] = current_count + 1

        probabilities = [(config, count / nshots) for config, count in counts.items()]
        return TaskProbabilities(probabilities=probabilities)
