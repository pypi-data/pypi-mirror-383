import os
import glob

import pytest

from bloqade.analog.task.batch import RemoteBatch
from bloqade.analog.atom_arrangement import Chain


def test_batch_error(*args):
    with pytest.raises(RemoteBatch.SubmissionException):
        (
            Chain(5, lattice_spacing=6.1)
            .rydberg.detuning.uniform.linear(-10, 10, 3.0)
            .quera.mock(submission_error=True)
            .run_async(100)
        )

    error_files = glob.glob("partial-batch-errors-*")
    batch_files = glob.glob("partial-batch-future-*")

    for error_file, batch_file in zip(error_files, batch_files):
        os.remove(error_file)
        os.remove(batch_file)

    assert len(error_files) == 1
    assert len(batch_files) == 1


def test_batch_warn():
    with pytest.warns():
        (
            Chain(5, lattice_spacing=6.1)
            .rydberg.detuning.uniform.linear(-10, 10, 3.0)
            .quera.mock(submission_error=True)
            .run_async(100, ignore_submission_error=True)
        )

    error_files = glob.glob("partial-batch-errors-*")
    batch_files = glob.glob("partial-batch-future-*")

    for error_file, batch_file in zip(error_files, batch_files):
        os.remove(error_file)
        os.remove(batch_file)

    assert len(error_files) == 1
    assert len(batch_files) == 1
