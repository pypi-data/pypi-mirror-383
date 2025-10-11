import pytest

from bloqade.analog.submission.ir.braket import to_braket_field


def test_to_braket_field_type_error():
    with pytest.raises(TypeError):
        to_braket_field("not a field type")
