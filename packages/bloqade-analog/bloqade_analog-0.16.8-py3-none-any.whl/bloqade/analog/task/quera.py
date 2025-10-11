import warnings
from dataclasses import field, dataclass

from beartype.typing import Any, Dict, Union, Optional

from bloqade.analog.serialize import Serializer
from bloqade.analog.task.base import Geometry, RemoteTask
from bloqade.analog.builder.base import ParamType
from bloqade.analog.submission.base import ValidationError
from bloqade.analog.submission.mock import MockBackend
from bloqade.analog.submission.quera import QuEraBackend
from bloqade.analog.submission.ir.parallel import ParallelDecoder
from bloqade.analog.submission.ir.task_results import (
    QuEraTaskResults,
    QuEraTaskStatusCode,
)
from bloqade.analog.submission.ir.task_specification import QuEraTaskSpecification


@dataclass
@Serializer.register
class QuEraTask(RemoteTask):
    task_id: Optional[str]
    backend: Union[QuEraBackend, MockBackend]
    task_ir: QuEraTaskSpecification
    metadata: Dict[str, ParamType]
    parallel_decoder: Optional[ParallelDecoder] = None
    task_result_ir: QuEraTaskResults = field(
        default_factory=lambda: QuEraTaskResults(
            task_status=QuEraTaskStatusCode.Unsubmitted
        )
    )

    def submit(self, force: bool = False) -> "QuEraTask":
        if not force:
            if self.task_id is not None:
                raise ValueError(
                    "the task is already submitted with %s" % (self.task_id)
                )

        self.task_id = self.backend.submit_task(self.task_ir)

        self.task_result_ir = QuEraTaskResults(task_status=QuEraTaskStatusCode.Enqueued)

        return self

    def validate(self) -> str:
        try:
            self.backend.validate_task(self.task_ir)
        except ValidationError as e:
            return str(e)

        return ""

    def fetch(self) -> "QuEraTask":
        # non-blocking, pull only when its completed
        if self.task_result_ir.task_status is QuEraTaskStatusCode.Unsubmitted:
            raise ValueError("Task ID not found.")

        if self.task_result_ir.task_status in [
            QuEraTaskStatusCode.Completed,
            QuEraTaskStatusCode.Partial,
            QuEraTaskStatusCode.Failed,
            QuEraTaskStatusCode.Unaccepted,
            QuEraTaskStatusCode.Cancelled,
        ]:
            return self

        status = self.status()
        if status in [QuEraTaskStatusCode.Completed, QuEraTaskStatusCode.Partial]:
            self.task_result_ir = self.backend.task_results(self.task_id)
        else:
            self.task_result_ir = QuEraTaskResults(task_status=status)

        return self

    def pull(self) -> "QuEraTask":
        # blocking, force pulling, even its completed
        if self.task_id is None:
            raise ValueError("Task ID not found.")

        self.task_result_ir = self.backend.task_results(self.task_id)

        return self

    def result(self) -> QuEraTaskResults:
        # blocking, caching

        if self.task_result_ir is None:
            pass
        else:
            if (
                self.task_id is not None
                and self.task_result_ir.task_status != QuEraTaskStatusCode.Completed
            ):
                self.pull()

        return self.task_result_ir

    def status(self) -> QuEraTaskStatusCode:
        if self.task_id is None:
            return QuEraTaskStatusCode.Unsubmitted

        return self.backend.task_status(self.task_id)

    def cancel(self) -> None:
        if self.task_id is None:
            warnings.warn("Cannot cancel task, missing task id.")
            return

        self.backend.cancel_task(self.task_id)

    @property
    def nshots(self):
        return self.task_ir.nshots

    def _geometry(self) -> Geometry:
        return Geometry(
            sites=self.task_ir.lattice.sites,
            filling=self.task_ir.lattice.filling,
            parallel_decoder=self.parallel_decoder,
        )

    def _result_exists(self) -> bool:
        if self.task_result_ir is None:
            return False
        else:
            if self.task_result_ir.task_status in [
                QuEraTaskStatusCode.Completed,
                QuEraTaskStatusCode.Partial,
            ]:
                return True
            else:
                return False

    # def submit_no_task_id(self) -> "HardwareTaskShotResults":
    #    return HardwareTaskShotResults(hardware_task=self)


@QuEraTask.set_serializer
def _serialze(obj: QuEraTask) -> Dict[str, ParamType]:
    return {
        "task_id": obj.task_id if obj.task_id is not None else None,
        "task_ir": obj.task_ir.dict(by_alias=True, exclude_none=True),
        "metadata": obj.metadata,
        "backend": {
            f"{obj.backend.__class__.__name__}": obj.backend.dict(
                exclude=set(["access_key", "secret_key", "session_token"])
            )
        },
        "parallel_decoder": (
            obj.parallel_decoder.dict() if obj.parallel_decoder else None
        ),
        "task_result_ir": obj.task_result_ir.dict() if obj.task_result_ir else None,
    }


@QuEraTask.set_deserializer
def _deserializer(d: Dict[str, Any]) -> QuEraTask:
    d["task_ir"] = QuEraTaskSpecification(**d["task_ir"])
    d["task_result_ir"] = (
        QuEraTaskResults(**d["task_result_ir"]) if d["task_result_ir"] else None
    )
    d["backend"] = (
        QuEraBackend(**d["backend"]["QuEraBackend"])
        if "QuEraBackend" in d["backend"]
        else MockBackend(**d["backend"]["MockBackend"])
    )
    d["parallel_decoder"] = (
        ParallelDecoder(**d["parallel_decoder"]) if d["parallel_decoder"] else None
    )
    return QuEraTask(**d)
