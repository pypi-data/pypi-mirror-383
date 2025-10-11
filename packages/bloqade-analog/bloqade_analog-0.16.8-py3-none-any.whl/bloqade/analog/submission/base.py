from typing import Union

from pydantic.v1 import Extra, BaseModel

from bloqade.analog.submission.ir.braket import BraketTaskSpecification
from bloqade.analog.submission.capabilities import get_capabilities
from bloqade.analog.submission.ir.capabilities import QuEraCapabilities
from bloqade.analog.submission.ir.task_results import (
    QuEraTaskResults,
    QuEraTaskStatusCode,
)
from bloqade.analog.submission.ir.task_specification import QuEraTaskSpecification


class ValidationError(Exception):
    pass


class SubmissionBackend(BaseModel):
    class Config:
        extra = Extra.forbid

    def get_capabilities(self, use_experimental: bool = False) -> QuEraCapabilities:
        return get_capabilities(use_experimental)

    def validate_task(
        self, task_ir: Union[BraketTaskSpecification, QuEraTaskSpecification]
    ) -> None:
        raise NotImplementedError

    def submit_task(
        self, task_ir: Union[BraketTaskSpecification, QuEraTaskSpecification]
    ) -> str:
        raise NotImplementedError

    def cancel_task(self, task_id: str) -> None:
        raise NotImplementedError

    def task_results(self, task_id: str) -> QuEraTaskResults:
        raise NotImplementedError

    def task_status(self, task_id: str) -> QuEraTaskStatusCode:
        raise NotImplementedError
