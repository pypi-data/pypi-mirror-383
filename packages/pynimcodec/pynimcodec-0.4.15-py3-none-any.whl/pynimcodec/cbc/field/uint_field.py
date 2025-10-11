"""Unsigned integer field class and methods."""

from typing import Optional

from pynimcodec.bitman import BitArray, append_bits_to_buffer, extract_from_buffer
from pynimcodec.utils import snake_case

from ..constants import FieldType
from .base_field import Field
from .calc import calc_decode, calc_encode

FIELD_TYPE = FieldType.UINT


class UintField(Field):
    """An unsigned integer field.
    
    Attributes:
        name (str): The unique field name.
        type (FieldType): The field type.
        description (str): Optional description for the field.
        optional (bool): Flag indicates if the field is optional in the message.
        size (int): The size of the encoded field in bits.
        encalc (str): Optional pre-encoding math expression to apply to value.
        decalc (str): Optional post-decoding math expression to apply to value.
        min (int): Optional minimum value to encode even if value is lower.
        max (int): Optional maximum value to encode even if value is higher.
    """
    
    def __init__(self, name: str, **kwargs) -> None:
        kwargs['type'] = FIELD_TYPE
        self._add_kwargs(['size'], ['encalc', 'decalc', 'min', 'max'])
        super().__init__(name, **kwargs)
        self._size: int = 0
        self._encalc: Optional[str] = None
        self._decalc: Optional[str] = None
        self._min: Optional[int] = None
        self._max: Optional[int] = None
        self.size = kwargs.pop('size')
        self.encalc = kwargs.pop('encalc', None)
        self.decalc = kwargs.pop('decalc', None)
        self.min = kwargs.pop('min', None)
        self.max = kwargs.pop('max', None)
        if self.min is not None and self.max is not None:
            if self.min >= self.max:
                raise ValueError('min must be lower than max')
    
    @property
    def size(self) -> int:
        return self._size
    
    @size.setter
    def size(self, value: int):
        if not isinstance(value, int) or value < 1:
            raise ValueError('Invalid size must be greater than 0.')
        self._size = value
    
    @property
    def encalc(self) -> str|None:
        return self._encalc
    
    @encalc.setter
    def encalc(self, expr: str|None):
        if expr is None or expr == '':
            self._encalc = None
        else:
            try:
                calc_encode(expr, -1)
                self._encalc = expr
            except TypeError as exc:
                raise ValueError('Invalid expression.') from exc
    
    @property
    def decalc(self) -> str|None:
        return self._decalc
    
    @decalc.setter
    def decalc(self, expr: str|None):
        if expr is None or expr == '':
            self._decalc = None
        else:
            try:
                calc_decode(expr, -1)
                self._decalc = expr
            except TypeError as exc:
                raise ValueError('Invalid expression.') from exc
    
    @property
    def _max_value(self) -> int:
        return 2**self.size - 1
    
    @property
    def min(self) -> 'int|None':
        return self._min
    
    @min.setter
    def min(self, value: int|None):
        if value is not None:
            if (not isinstance(value, int) or
                value < 0 or
                value > self._max_value):
                raise ValueError('min must be within range' +
                                 f' [0..{self._max_value}]')
            if self.max is not None and value > self.max:
                raise ValueError('min must be below max')
        self._min = value
    
    @property
    def max(self) -> int|None:
        return self._max
    
    @max.setter
    def max(self, value: int|None):
        if value is not None:
            if (not isinstance(value, int) or
                value < 1 or
                value > self._max_value):
                raise ValueError('max must be within range' +
                                 f' [1..{self._max_value}]')
            if self.min is not None and value < self.min:
                raise ValueError('max must be above min')
        self._max = value
    
    def decode(self, buffer: bytes, offset: int) -> tuple[int|float, int]:
        """Extracts the unsigned integer value from a buffer."""
        return decode(self, buffer, offset)
    
    def encode(self,
               value: int|float,
               buffer: bytearray,
               offset: int,
               ) -> tuple[bytearray, int]:
        "Appends the unsigned integer value to the buffer at the bit offset."
        return encode(self, value, buffer, offset)


def create(**kwargs) -> UintField:
    """Create an UintField."""
    return UintField(**{snake_case(k): v for k, v in kwargs.items()})


def decode(field: Field, buffer: bytes, offset: int) -> tuple[int|float, int]:
    """Decode an unsigned integer field value from a buffer at a bit offset.
    
    If the field has `decalc` attribute populated it will apply the math
    expression.
    
    Args:
        field (Field): The field definition, with `size` attribute.
        buffer (bytes): The encoded buffer to extract from.
        offset (int): The bit offset to extract from.
    
    Returns:
        tuple(int|float, int): The decoded value and the offset of the next
            field in the buffer.
    
    Raises:
        ValueError: If field is invalid.
    """
    if not isinstance(field, UintField):
        raise ValueError('Invalid field definition.')
    enc: int = extract_from_buffer(buffer, offset, field.size) # type: ignore
    value = calc_decode(field.decalc, enc) if field.decalc else enc
    return ( value, offset + field.size )


def encode(field: UintField,
           value: int|float,
           buffer: bytearray,
           offset: int,
           ) -> tuple[bytearray, int]:
    """Append an unsigned integer field value to a buffer at a bit offset.
    
    Args:
        field (IntField): The field definition.
        value (int|float): The value to encode. Floats are only allowed if
            'encalc' specifies an integer conversion.
        buffer (bytearray): The buffer to modify/append to.
        offset (int): The bit offset to append from.
    
    Returns:
        tuple(bytearray, int): The modified buffer and the offset of the next
            field.
    
    Raises:
        ValueError: If the field or value is invalid for the field definition.
    """
    if not isinstance(field, UintField):
        raise ValueError('Invalid UintField definition.')
    if ((not isinstance(value, int) and
         not (isinstance(value, float) and field.encalc)) or value < 0):
        raise ValueError(f'Invalid {field.name} value.')
    if field.encalc:
        value = calc_encode(field.encalc, value)
    elif not isinstance(value, int):
        raise ValueError(f'Invalid {field.name} value.')
    if field.min is not None and value < field.min:
        value = field.min
    if field.max is not None and value > field.max:
        value = field.max
    if value > field._max_value:
        raise ValueError(f'{field.name} must be <= {field._max_value}.')
    bits = BitArray.from_int(value, field.size)
    return ( append_bits_to_buffer(bits, buffer, offset), offset + field.size )
