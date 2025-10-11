import pytest

from bloqade.analog import start
from bloqade.analog.serialize import dumps, loads
from bloqade.analog.task.quera import QuEraTask
from bloqade.analog.task.braket import BraketTask
from bloqade.analog.submission.quera import QuEraBackend
from bloqade.analog.submission.braket import BraketBackend


def test_quera_task():
    backend = QuEraBackend(api_hostname="a", qpu_id="b")
    task = QuEraTask(
        task_ir=None, task_id=None, metadata={}, backend=backend, parallel_decoder=None
    )

    with pytest.raises(ValueError):
        task.fetch()

    assert task._result_exists() is False

    with pytest.raises(ValueError):
        task.pull()


def test_braket_task():
    backend = BraketBackend()
    task = BraketTask(
        task_ir=None, task_id=None, metadata={}, backend=backend, parallel_decoder=None
    )

    with pytest.raises(ValueError):
        task.fetch()

    assert task._result_exists() is False

    with pytest.raises(ValueError):
        task.pull()


def test_braket_batch():
    program = (
        start.add_position((0, 0))
        .rydberg.rabi.amplitude.uniform.piecewise_linear(
            durations=[0.05, 1, 0.05], values=[0.0, 15.8, 15.8, 0.0]
        )
        .detuning.uniform.piecewise_linear(durations=[1.1], values=[0.0, 0.0])
    )

    output = program.braket.aquila()._compile(10)

    output_str = dumps(output)
    assert isinstance(loads(output_str), type(output))
    assert loads(output_str).tasks == output.tasks
    assert loads(output_str).name == output.name


#
# batch = RemoteBatch.from_json(...)
# batch.fetch() # update results,
#               # this is non-blocking.
#               # It only pull results if the remote job complete

# batch.pull() # this is blocking. it will hanging there waiting for job to complete.
# batch.to_json(...)

# # Get finished tasks (not nessasry sucessfully completed)
# finished_batch = batch.get_finished_tasks()

# # Get complete tasks (sucessfully completed)
# completed_batch = batch.get_completed_tasks()

# # Remove failed tasks:
# new_batch = batch.remove_failed_tasks()
