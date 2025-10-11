from decimal import Decimal
from numbers import Real

from beartype.typing import List, Union

from bloqade.analog.ir.scalar import Scalar

ScalarType = Union[Real, Decimal, str, Scalar]
LiteralType = Union[Real, Decimal]
ParamType = Union[LiteralType, List[LiteralType]]
