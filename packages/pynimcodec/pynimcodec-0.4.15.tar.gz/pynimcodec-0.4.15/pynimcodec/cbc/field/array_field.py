"""Array field class and methods."""

from typing import Any

from pynimcodec.bitman import (
    append_bits_to_buffer,
    append_bytes_to_buffer,
    extract_from_buffer,
)
from pynimcodec.utils import snake_case

from ..constants import FieldType
from .base_field import Field, Fields
from .field_length import decode_field_length, encode_field_length

FIELD_TYPE = FieldType.ARRAY


class ArrayField(Field):
    """An array field.
    
    Attributes:
        name (str): The unique field name.
        type (FieldType): The field type.
        description (str): Optional description for the field.
        optional (bool): Flag indicates if the field is optional in the message.
        size (int): The maximum size of the array (elements/rows).
        fixed (bool): Flag indicating if the array is a fixed size.
        fields (Field[]): A list of fields defining columns of the array.
    """
    
    def __init__(self, name: str, **kwargs) -> None:
        kwargs['type'] = FIELD_TYPE
        self._add_kwargs(['size', 'fields'], ['fixed'])
        super().__init__(name, **kwargs)
        self._size: int = 0
        self._fixed: bool = False
        self._fields: Fields = Fields()
        self.size = kwargs.pop('size')
        self.fixed = kwargs.pop('fixed', False)
        self.fields = kwargs.pop('fields')
    
    @property
    def size(self) -> int:
        return self._size
    
    @size.setter
    def size(self, value: int):
        if not isinstance(value, int) or value < 1:
            raise ValueError('Invalid size must be greater than 0.')
        self._size = value
    
    @property
    def fixed(self) -> bool:
        return self._fixed
    
    @fixed.setter
    def fixed(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError('Invalid value for fixed.')
        self._fixed = value
    
    @property
    def fields(self) -> Fields:
        return self._fields
    
    @fields.setter
    def fields(self, fields: Fields|list[Field]):
        if (not isinstance(fields, (Fields, list)) or
            not all(isinstance(x, Field) for x in fields)):
            raise ValueError('Invalid list of fields')
        self._fields = Fields(fields)
    
    def decode(self, buffer: bytes, offset: int) -> tuple[list[Any], int]:
        """Extracts the array value from a buffer."""
        return decode(self, buffer, offset)
    
    def encode(self,
               value: list[Any],
               buffer: bytearray,
               offset: int,
               ) -> tuple[bytearray, int]:
        "Appends the array value to the buffer at the bit offset."
        return encode(self, value, buffer, offset)


def create(**kwargs) -> ArrayField:
    """Create a ArrayField."""
    return ArrayField(**{snake_case(k): v for k, v in kwargs.items()})


def decode(field: Field, buffer: bytes, offset: int) -> tuple[list[Any], int]:
    """Decode an array field value from a buffer at a bit offset.
    
    Args:
        field (Field): The field definition, with `size` attribute.
        buffer (bytes): The encoded buffer to extract from.
        offset (int): The bit offset to extract from.
    
    Returns:
        tuple(list, int): The decoded list and the offset of the next
            field in the buffer.
    
    Raises:
        ValueError: If field is invalid.
    """
    if not isinstance(field, ArrayField):
        raise ValueError('Invalid ArrayField definition.')
    if not field.fixed:
        rows, offset = decode_field_length(buffer, offset)
    else:
        rows = field.size
    value = []
    while len(value) < rows:
        decoded = {} if len(field.fields) > 1 else None
        for col in field.fields:
            if col.optional:
                present = extract_from_buffer(buffer, offset, 1) == 1
                offset += 1
                if not present:
                    continue
            if len(field.fields) == 1:
                decoded, offset = col.decode(buffer, offset)
            elif isinstance(decoded, dict):
                decoded[col.name], offset = col.decode(buffer, offset)
        value.append(decoded)
    return ( value, offset )


def encode(field: ArrayField,
           value: list[Any],
           buffer: bytearray,
           offset: int,
           ) -> tuple[bytearray, int]:
    """Append an array field values to a buffer at a bit offset.
    
    Args:
        field (IntField): The field definition.
        value (list): The array values to encode (rows of Field columns).
        buffer (bytearray): The buffer to modify/append to.
        offset (int): The bit offset to append from.
    
    Returns:
        tuple(bytearray, int): The modified buffer and the offset of the next
            field.
    
    Raises:
        ValueError: If the field or value is invalid for the field definition.
    """
    if not isinstance(field, ArrayField):
        raise ValueError('Invalid ArrayField definition.')
    if (not isinstance(value, list) or not value or
        field.fixed and len(value) < field.size):
        raise ValueError(f'Invalid {field.name} value array.')
    tmp_buffer = bytearray()
    tmp_offset = 0
    for i, row in enumerate(value):
        for col in field.fields:
            if col.optional:
                present = 1 if not isinstance(row, dict) or col.name in row else 0
                tmp_buffer = append_bits_to_buffer(
                    [present], tmp_buffer, tmp_offset   # type: ignore
                )
                tmp_offset += 1
                if not present:
                    continue
            if not isinstance(row, dict):
                if len(field.fields) > 1:
                    raise ValueError(f'{field.name} row {i} missing column keys')
                tmp_buffer, tmp_offset = col.encode(row, tmp_buffer, tmp_offset)
            else:
                if col.name not in row:
                    raise ValueError(f'{field.name} row {i} missing {col.name}')
                tmp_buffer, tmp_offset = col.encode(row[col.name], tmp_buffer, tmp_offset)
    if not field.fixed:
        buffer, offset = encode_field_length(len(value), buffer, offset)
    buffer = append_bytes_to_buffer(bytes(tmp_buffer), buffer, offset)
    return ( buffer, offset + len(tmp_buffer) )
