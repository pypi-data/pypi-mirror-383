import warnings

from braket.aws import AwsDevice, AwsQuantumTask
from pydantic.v1 import PrivateAttr
from beartype.typing import Optional

import bloqade.analog
from bloqade.analog.submission.base import SubmissionBackend
from bloqade.analog.submission.ir.braket import (
    to_braket_task,
    to_quera_capabilities,
    from_braket_status_codes,
    from_braket_task_results,
)
from bloqade.analog.submission.ir.capabilities import QuEraCapabilities
from bloqade.analog.submission.ir.task_results import (
    QuEraTaskResults,
    QuEraTaskStatusCode,
)
from bloqade.analog.submission.ir.task_specification import QuEraTaskSpecification


class BraketBackend(SubmissionBackend):
    device_arn: str = "arn:aws:braket:us-east-1::device/qpu/quera/Aquila"
    _device: Optional[AwsDevice] = PrivateAttr(default=None)

    @property
    def device(self) -> AwsDevice:
        if self._device is None:
            self._device = AwsDevice(self.device_arn)
            user_agent = f"Bloqade/{bloqade.analog.__version__}"
            self._device.aws_session.add_braket_user_agent(user_agent)

        return self._device

    def get_capabilities(self, use_experimental: bool = False) -> QuEraCapabilities:
        from botocore.exceptions import ClientError, BotoCoreError

        if use_experimental:
            return super().get_capabilities(use_experimental)

        try:
            return to_quera_capabilities(self.device.properties.paradigm)
        except BotoCoreError:
            warnings.warn(
                "Could not retrieve device capabilities from braket API. "
                "Using local capabilities file for Aquila."
            )
        except ClientError:
            warnings.warn(
                "Could not retrieve device capabilities from braket API. "
                "Using local capabilities file for Aquila."
            )

        return super().get_capabilities()

    def submit_task(self, task_ir: QuEraTaskSpecification) -> str:
        shots, ahs_program = to_braket_task(task_ir)
        task = self.device.run(ahs_program, shots=shots)
        return task.id

    def task_results(self, task_id: str) -> QuEraTaskResults:
        return from_braket_task_results(AwsQuantumTask(task_id).result())

    def cancel_task(self, task_id: str) -> None:
        AwsQuantumTask(task_id).cancel()

    def task_status(self, task_id: str) -> QuEraTaskStatusCode:
        return from_braket_status_codes(AwsQuantumTask(task_id).state())

    def validate_task(self, task_ir: QuEraTaskSpecification):
        pass

    # def validate_task(self, task_ir: QuEraTaskSpecification):
    #     try:
    #         task_id = self.submit_task(task_ir)
    #     except Exception as e:
    #         if "ValidationException" in str(e) and "validation error" in str(e):
    #             raise ValidationError(str(e))
    #         else:
    #             raise e

    #     # don't want the task to actually run
    #     try:
    #         self.cancel_task(task_id)
    #     except Exception as e:
    #         return
