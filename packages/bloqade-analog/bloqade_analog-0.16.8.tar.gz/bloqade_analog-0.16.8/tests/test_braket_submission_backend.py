from unittest.mock import patch

import pytest

import bloqade.analog.submission.braket
import bloqade.analog.submission.ir.task_specification as task_spec
from bloqade.analog.submission.base import ValidationError
from bloqade.analog.submission.ir.task_results import QuEraTaskStatusCode


def get_task_ir():
    return task_spec.QuEraTaskSpecification(
        nshots=10,
        lattice=task_spec.Lattice(sites=[(0, 0)], filling=[1]),
        effective_hamiltonian=task_spec.EffectiveHamiltonian(
            rydberg=task_spec.RydbergHamiltonian(
                rabi_frequency_amplitude=task_spec.RabiFrequencyAmplitude(
                    global_=task_spec.GlobalField(
                        times=[0, 1e-6, 2e-6, 3e-6, 4e-6],
                        values=[0, 15e6, 15e6, 0],
                    )
                ),
                rabi_frequency_phase=task_spec.RabiFrequencyPhase(
                    global_=task_spec.GlobalField(
                        times=[0, 4e-6],
                        values=[0, 0],
                    )
                ),
                detuning=task_spec.Detuning(
                    global_=task_spec.GlobalField(
                        times=[0, 1e-6, 2e-6, 3e-6, 4e-6],
                        values=[0, 15e6, 15e6, 0],
                    )
                ),
            )
        ),
    )


@patch("bloqade.analog.submission.braket.AwsDevice")
def test_braket_submit(*args, **kwargs):
    task_ir = get_task_ir()

    backend = bloqade.analog.submission.braket.BraketBackend()
    mock_aws_device = bloqade.analog.submission.braket.AwsDevice(backend.device_arn)

    backend.submit_task(task_ir)

    mock_aws_device.run.assert_called_once()


@patch("bloqade.analog.submission.braket.AwsDevice")
def test_add_braket_user_agent_invoked(*args, **kwargs):
    backend = bloqade.analog.submission.braket.BraketBackend()
    expected_user_agent = f"Bloqade/{bloqade.analog.__version__}"

    backend.device.aws_session.add_braket_user_agent.assert_called_with(
        expected_user_agent
    )


@pytest.mark.skip(
    reason="removed implementation for validation because of issue with empty queue."
)
@patch("bloqade.analog.submission.braket.AwsDevice")
@patch("bloqade.analog.submission.braket.AwsQuantumTask")
def test_braket_validate_task(*args, **kwargs):
    task_ir = get_task_ir()

    backend = bloqade.analog.submission.braket.BraketBackend()
    mock_aws_device = bloqade.analog.submission.braket.AwsDevice(backend.device_arn)
    mock_aws_device.run.return_value = bloqade.analog.submission.braket.AwsQuantumTask(
        "task_id"
    )
    mock_aws_device.run.return_value.id = "task_id"

    # test passing validation
    backend.validate_task(task_ir)

    mock_aws_device.run.assert_called_once()
    mock_aws_device.run.return_value.cancel.assert_called_once()

    mock_aws_device.reset_mock()

    # test failing validation
    mock_aws_device = bloqade.analog.submission.braket.AwsDevice(backend.device_arn)
    mock_aws_device.run.side_effect = Exception("ValidationException: validation error")
    with pytest.raises(ValidationError):
        backend.validate_task(task_ir)

    mock_aws_device.run.assert_called_once()

    mock_aws_device.reset_mock()

    # test failing validation
    mock_aws_device = bloqade.analog.submission.braket.AwsDevice(backend.device_arn)
    mock_aws_device.run.side_effect = Exception("other error")
    with pytest.raises(Exception):
        backend.validate_task(task_ir)

    mock_aws_device.run.assert_called_once()


@patch("bloqade.analog.submission.braket.AwsQuantumTask")
def test_braket_fetch(*args, **kwargs):
    backend = bloqade.analog.submission.braket.BraketBackend()
    mock_aws_quantum_task = bloqade.analog.submission.braket.AwsQuantumTask("task_id")

    backend.task_results("task_id")

    mock_aws_quantum_task.result.assert_called_once()


@patch("bloqade.analog.submission.braket.AwsQuantumTask")
def test_braket_cancel(*args, **kwargs):
    backend = bloqade.analog.submission.braket.BraketBackend()
    mock_aws_quantum_task = bloqade.analog.submission.braket.AwsQuantumTask("task_id")

    backend.cancel_task("task_id")

    mock_aws_quantum_task.cancel.assert_called_once()


@patch("bloqade.analog.submission.braket.AwsQuantumTask")
def test_braket_status(*args, **kwargs):
    backend = bloqade.analog.submission.braket.BraketBackend()
    mock_aws_quantum_task = bloqade.analog.submission.braket.AwsQuantumTask("task_id")
    mock_aws_quantum_task.state.side_effect = [
        "CREATED",
        "RUNNING",
        "COMPLETED",
        "FAILED",
        "CANCELLED",
        "QUEUED",
        "ASDLFKASLDF",
    ]

    assert backend.task_status("task_id") == QuEraTaskStatusCode.Created
    assert backend.task_status("task_id") == QuEraTaskStatusCode.Running
    assert backend.task_status("task_id") == QuEraTaskStatusCode.Completed
    assert backend.task_status("task_id") == QuEraTaskStatusCode.Failed
    assert backend.task_status("task_id") == QuEraTaskStatusCode.Cancelled
    assert backend.task_status("task_id") == QuEraTaskStatusCode.Enqueued
    with pytest.raises(ValueError):
        backend.task_status("task_id")
