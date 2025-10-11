"""Boolean field class and methods."""

from pynimcodec.bitman import append_bits_to_buffer, extract_from_buffer
from pynimcodec.utils import snake_case

from ..constants import FieldType
from .base_field import Field

FIELD_TYPE = FieldType.BOOL


class BoolField(Field):
    """A boolean field.
    
    Attributes:
        name (str): The unique field name.
        type (FieldType): The field type.
        description (str): Optional description for the field.
        optional (bool): Flag indicates if the field is optional in the message.
    """
    
    def __init__(self, name: str, **kwargs) -> None:
        kwargs['type'] = FIELD_TYPE
        super().__init__(name, **kwargs)
    
    def decode(self, buffer: bytes, offset: int) -> tuple[bool, int]:
        """Extracts the boolean value from a buffer."""
        return decode(self, buffer, offset)
    
    def encode(self,
               value: bool|int,
               buffer: bytearray,
               offset: int,
               ) -> tuple[bytearray, int]:
        "Appends the boolean value to the buffer at the bit offset."
        return encode(self, value, buffer, offset)


def create(**kwargs) -> BoolField:
    """Create a BoolField."""
    return BoolField(**{snake_case(k): v for k, v in kwargs.items()})


def decode(field: Field, buffer: bytes, offset: int) -> tuple[bool, int]:
    """Decode a boolean field value from a buffer at a bit offset.
    
    Args:
        field (Field): The field definition, with `size` attribute.
        buffer (bytes): The encoded buffer to extract from.
        offset (int): The bit offset to extract from.
    
    Returns:
        tuple(bool, int): The decoded value and the offset of the next
            field in the buffer.
    
    Raises:
        ValueError: If field is invalid.
    """
    if not isinstance(field, BoolField):
        raise ValueError('Invalid BoolField definition.')
    value = extract_from_buffer(buffer, offset, 1)
    return ( bool(value), offset + 1 )


def encode(field: BoolField,
           value: bool|int,
           buffer: bytearray,
           offset: int,
           ) -> tuple[bytearray, int]:
    """Append a boolean field value to a buffer at a bit offset.
    
    Args:
        field (IntField): The field definition.
        value (bool): The value to encode.
        buffer (bytearray): The buffer to modify/append to.
        offset (int): The bit offset to append from.
    
    Returns:
        tuple(bytearray, int): The modified buffer and the offset of the next
            field.
    
    Raises:
        ValueError: If the field or value is invalid for the field definition.
    """
    if not isinstance(field, BoolField):
        raise ValueError('Invalid BoolField definition.')
    if not isinstance(value, bool):
        if value in [0, 1]:
            value = bool(value)
        else:
            raise ValueError(f'Invalid {field.name} boolean value.')
    return ( append_bits_to_buffer([int(value)], buffer, offset), offset + 1 ) # type: ignore
