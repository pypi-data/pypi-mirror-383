"""Struct field class and methods."""

from typing import Any

from pynimcodec.utils import snake_case

from ..constants import FieldType
from .base_field import Field, Fields, decode_fields, encode_fields

FIELD_TYPE = FieldType.STRUCT


class StructField(Field):
    """A data structure field.
    
    Attributes:
        name (str): The unique field name.
        type (FieldType): The field type.
        description (str): Optional description for the field.
        optional (bool): Flag indicates if the field is optional in the message.
        fields (Field[]): The list of fields making up the structure.
    """
    
    def __init__(self, name: str, **kwargs) -> None:
        kwargs['type'] = FIELD_TYPE
        self._add_kwargs(['fields'], [])
        super().__init__(name, **kwargs)
        self._fields: Fields = Fields()
        self.fields = kwargs.pop('fields')
    
    @property
    def fields(self) -> Fields:
        return self._fields
    
    @fields.setter
    def fields(self, fields: Fields|list[Field]):
        if (not isinstance(fields, (Fields, list)) or
            not all(isinstance(x, Field) for x in fields)):
            raise ValueError('Invalid list of fields')
        self._fields = Fields(fields)

    def decode(self, buffer: bytes, offset: int) -> tuple[dict[str, Any], int]:
        """Extracts the struct value from a buffer."""
        return decode(self, buffer, offset)
    
    def encode(self,
               value: dict[str, Any],
               buffer: bytearray,
               offset: int,
               ) -> tuple[bytearray, int]:
        "Appends the struct value to the buffer at the bit offset."
        return encode(self, value, buffer, offset)


def create(**kwargs) -> StructField:
    """Create a StructField."""
    return StructField(**{snake_case(k): v for k, v in kwargs.items()})


def decode(field: Field, buffer: bytes, offset: int) -> tuple[dict[str, Any], int]:
    """Decode a struct field value from a buffer at a bit offset.
    
    Args:
        field (Field): The field definition, with `size` attribute.
        buffer (bytes): The encoded buffer to extract from.
        offset (int): The bit offset to extract from.
    
    Returns:
        tuple(dict, int): The decoded value and the offset of the next
            field in the buffer.
    
    Raises:
        ValueError: If field is invalid.
    """
    if not isinstance(field, StructField):
        raise ValueError('Invalid StructField definition.')
    value, offset = decode_fields(field, buffer, offset)
    return ( value, offset )


def encode(field: StructField,
           value: dict[str, Any],
           buffer: bytearray,
           offset: int,
           ) -> tuple[bytearray, int]:
    """Append a struct field value to a buffer at a bit offset.
    
    Args:
        field (IntField): The field definition.
        value (dict): The structure to encode.
        buffer (bytearray): The buffer to modify/append to.
        offset (int): The bit offset to append from.
    
    Returns:
        tuple(bytearray, int): The modified buffer and the offset of the next
            field.
    
    Raises:
        ValueError: If the field or value is invalid for the field definition.
    """
    if not isinstance(field, StructField):
        raise ValueError('Invalid StructField definition.')
    return encode_fields(value, field, buffer, offset)
