"""Compact Binary Codec Message class and methods."""

import logging
from enum import Enum
from typing import Any

import aiocoap

from pynimcodec.bitman import append_bytes_to_buffer
from pynimcodec.cbc.codec.base_codec import CbcCodec, CodecList
from pynimcodec.cbc.constants import MessageDirection
from pynimcodec.cbc.field.base_field import Field, Fields, decode_fields, encode_fields
from pynimcodec.cbc.field.common import create_field
from pynimcodec.utils import camel_case, snake_case

_log = logging.getLogger(__name__)


class Message(CbcCodec):
    """A message data structure.
    
    Attributes:
        name (str): The unique message name within a set.
        description (str): Optional description for the intended message use.
        direction (MessageDirection): Indicates Mobile-Originated/Uplink or
            Mobile-Terminated/Downlink
        message_key (int): 16-bit direction-unique message key
            within a superset.
        fields (Fields)
    """
    
    def __init__(self,
                 name: str,
                 direction: MessageDirection,
                 message_key: int,
                 fields: Fields,
                 **kwargs) -> None:
        """Create a message codec.
        
        Args:
            name (str): The unique message name within a set.
            direction (MessageDirection): The direction of communication
                (required)
            message_key (int): The 16-bit direction-unique message key.
            fields (Fields): The ordered list of Field codec definitions.
            **description (str): Optional description of intended use.
        """
        self._add_kwargs(['direction', 'message_key', 'fields'],
                         ['coap_compatible', 'v_reserved', 'nimo_compatible'])
        kwargs['direction'] = direction
        kwargs['message_key'] = message_key
        kwargs['fields'] = fields
        super().__init__(name, **kwargs)
        self._direction: MessageDirection = direction
        assert isinstance(self._direction, MessageDirection)
        self._message_key: int = message_key
        assert isinstance(self._message_key, int)
        assert self._message_key in range(0, 2**16)
        self._fields: Fields = fields
        assert isinstance(self._fields, Fields)
        # coap_compatible can be False to allow message_key values that may
        #  be misinterpreted as CoAP if sent without CoAP header
        self._coap_compatible: bool = kwargs.get('coap_compatible', True)
        # o_reserved True allows override of operator-reserved message_key values
        self._o_reserved: bool = kwargs.get('o_reserved', False)
    
    @property
    def direction(self) -> MessageDirection:
        return self._direction
    
    @direction.setter
    def direction(self, value: 'MessageDirection|str'):
        if isinstance(value, str):
            if value in [e.value for e in MessageDirection]:
                value = MessageDirection(value)
        if not isinstance(value, MessageDirection):
            raise ValueError('Invalid direction type')
        self._direction = value
    
    @property
    def message_key(self) -> int:
        return self._message_key
    
    @message_key.setter
    def message_key(self, value: int):
        if not isinstance(value, int) or value not in range(0, 2**16):
            raise ValueError('message_key must be a 16-bit unsigned integer')
        if self._coap_compatible and value < 32768:
            _log.warning('message_key conflict with CoAP compatibility')
        if not self._o_reserved and value > 65279:
            _log.warning('message_key conflict with operator-reserved range')
        self._message_key = value

    @property
    def fields(self) -> Fields:
        return self._fields
    
    @fields.setter
    def fields(self, fields: Fields):
        if (not isinstance(fields, Fields)):
            raise ValueError('Invalid list of fields')
        self._fields = fields
    
    def to_json(self):
        """Get a JSON representation of the message codec."""
        key_order = ['name', 'direction', 'message_key', 'description', 'fields']
        raw = {}
        for attr_name in dir(self.__class__):
            if (not isinstance(getattr(self.__class__, attr_name), property) or
                attr_name.startswith('_') or
                getattr(self, attr_name) is None or
                getattr(self, attr_name) in ['']):
                # skip
                continue
            elif isinstance(getattr(self, attr_name), Fields):
                raw[attr_name] = []
                for fld in getattr(self, attr_name):
                    raw[attr_name].append(fld.to_json())
            elif (issubclass(getattr(self, attr_name).__class__, Enum)):
                raw[attr_name] = getattr(self, attr_name).value
            else:
                raw[attr_name] = getattr(self, attr_name)
        reordered = {}
        reordered = { camel_case(k): raw[k] for k in key_order if k in raw }
        remaining = { camel_case(k): raw[k] for k in raw if k not in key_order }
        reordered.update(remaining)
        return reordered

    @classmethod
    def from_json(cls, content: dict) -> 'Message':
        """Create a field from a JSON-style content dictionary."""
        if not isinstance(content, dict) or not content:
            raise ValueError('Invalid content.')
        return cls(**{snake_case(k): v for k, v in content.items()})
    
    def encode(self, content: dict, **kwargs):
        """Encode the message from a dictionary definition."""
        return encode_message(content, message=self, **kwargs)
    
    def decode(self, buffer: bytes, **kwargs):
        """Decode the message from a buffer."""
        return decode_message(buffer, message=self, **kwargs)
    

class Messages(CodecList[Message]):
    """Container class for a list of Message codecs with unique names."""
    
    def __init__(self, *args) -> None:
        super().__init__(Message, *args)
    
    def append(self, codec: Message):
        """Append uniquely named Message codec to the end of the list.
        
        Args:
            codec (Message): The message codec.
        
        Raises:
            ValueError: If duplicate `message_key` for the direction, or
                duplicate `name` in the list.
        """
        for mc in self:
            if (mc.message_key == codec.message_key and
                mc.direction == codec.direction):
                raise ValueError(f'Duplicate {mc.direction.name} message_key')
        return super().append(codec)
    
    def by_key(self, message_key: int, direction: MessageDirection) -> Message:
        """Get a Message using message_key and direction."""
        if message_key not in range(0, 2**16):
            raise ValueError('Invalid message_key must be 16-bit unsigned int')
        if isinstance(direction, str):
            try:
                direction = MessageDirection(direction)
            except ValueError as exc:
                raise ValueError('Invalid message direction') from exc
        if not isinstance(direction, MessageDirection):
            raise ValueError('Invalid direction')
        for m in self:
            if m.message_key == message_key and m.direction == direction:
                return m
        raise ValueError('message_key and direction not found')
    
    def decode(self, buffer: bytes, **kwargs) -> dict:
        """Decode a message from a buffer.
        
        Args:
            buffer (bytes): The buffer to decode from.
            **name (str): The unique name of the message in Messages. If not
                specified must set `direction` and any of `message_key`, `nim`,
                or `coap`.
            **direction (MessageDirection|str): The message direction is
                required if unique `name` is not specified.
            **message_key (int): May be supplied instead of `name`. Must be
                accompanied by `direction`.
            **nim (bool): Indicates the buffer begins with the 2-byte
                `message_key`.
            **coap (bool): Indicates the buffer includes CoAP header.
            **incl_dir (bool): If set, include `direction` in output.
            **incl_key (bool): If set, include `message_key` in output.
            **incl_desc (bool): If set, include `description` in output.
            
        """
        if not isinstance(buffer, (bytes, bytearray)) or len(buffer) == 0:
            raise ValueError('Invalid buffer')
        return decode_message(buffer, messages=self, **kwargs)
    
    def encode(self, content: dict, **kwargs) -> bytes|aiocoap.Message:
        """Encodes a message based on content in a dictionary.
        
        Args:
            content (dict): The message content to encode. Must include keys
                `name` (str) and `value` (list)
            **nim (bool): Optional flag indicating to apply `message_key` as
                the first 2 bytes of NIM message overhead
            **coap (bool): Optional flag indicating to generate CoAP overhead
                using `message_key` as the MessageID in header
        
        Returns:
            bytes: The encoded message buffer.
        
        Raises:
            ValueError: If the content is invalid or both `nim` and `coap` flags
                are set.
        """
        return encode_message(content, messages=self, **kwargs)


def create_message(obj: dict) -> Message:
    """Creates a Message from a dictionary definition."""
    if not isinstance(obj, dict):
        raise ValueError('Invalid object to create Message.')
    if 'fields' not in obj or not isinstance(obj['fields'], (list, Fields)):
        raise ValueError('Invalid fields definition')
    for i, field in enumerate(obj['fields']):
        if not isinstance(field, Field):
            obj['fields'][i] = create_field(field)
    obj['fields'] = Fields(obj['fields'])
    obj['direction'] = MessageDirection(obj['direction'])
    return Message(**{snake_case(k): v for k, v in obj.items()})


def decode_message(buffer: bytes, **kwargs) -> dict[str, Any]:
    """Decodes a Message from a data buffer.
    
    Which Message codec to use is determined by parsing either the first two
    bytes of Non-IP over-the-air data received, or the 3rd-4th bytes if using
    Constrained Application Protocol (CoAP) transport.
    
    Args:
        buffer (bytes): The data buffer containing the message payload.
            May include NIM or CoAP header bytes.
        **messages (Messages): The messages codec list to use for decoding.
            Must be present if not using `message`.
        **message (Message): The message codec to use for decoding.
            Must be present if notusing `messages`.
        **name (str): The unique name of the message in Messages. If not
            specified must set `direction` and any of `message_key`, `nim`,
            or `coap`.
        **direction (MessageDirection|str): The message direction is
            required if unique `name` is not specified.
        **message_key (int): May be supplied instead of `name`. Must be
            accompanied by `direction`.
        **nim (bool): Indicates the buffer begins with the 2-byte
            `message_key`.
        **coap (bool): Indicates the buffer includes CoAP header.
        **incl_dir (bool): If set, include `direction` in output.
        **incl_key (bool): If set, include `message_key` in output.
        **incl_desc (bool): If set, include `description` in output.
    
    Returns:
        dict: The decoded message structure.
    """
    if not isinstance(buffer, (bytes, bytearray)) or len(buffer) == 0:
        raise ValueError('Invalid data buffer.')
    messages = kwargs.get('messages')
    if messages and not isinstance(messages, Messages):
        raise ValueError('Invalid Messages codec list.')
    message = kwargs.get('message')
    if message and not isinstance(message, Message):
        raise ValueError('Invalid Message codec.')
    name = kwargs.get('name')
    direction = kwargs.get('direction')
    message_key = kwargs.get('message_key')
    nim = kwargs.get('nim') is True
    coap = kwargs.get('coap') is True
    offset = 0   # starting bit offset to read buffer from
    if not message and messages:
        if name:
            message = messages[name]
        else:
            if isinstance(direction, str):
                try:
                    direction = MessageDirection(direction)
                except ValueError as exc:
                    raise ValueError('Invalid message direction') from exc
            if not direction:
                raise ValueError('direction required when name not provided')
            if message_key:
                if message_key not in range(0, 2**16):
                    raise ValueError('message_key must be 16-bit unsigned int')
                for m in messages:
                    if m.message_key == message_key and m.direction == direction:
                        message = m
                        break
    coap_message = None
    if nim:
        if coap:
            raise ValueError('nim and coap flags mutually exclusive')
        message_key = int.from_bytes(buffer[0:2], 'big')
        offset = 16
    elif coap:
        coap_message = aiocoap.Message.decode(buffer)
        message_key = coap_message.mid
        buffer = coap_message.payload
    else:
        _log.info('No framing specified - decoding raw payload no headers')
    if not message and messages:
        assert isinstance(message_key, int) and message_key in range(0, 65536)
        assert isinstance(direction, MessageDirection)
        message = messages.by_key(message_key, direction)
    assert message is not None
    if message_key and message_key != message.message_key:
        raise ValueError('Mismatch between provided/derived message_key')
    decoded = { 'name': message.name }
    if kwargs.get('incl_dir') is True:
        decoded['direction'] = message.direction.value
    if kwargs.get('incl_key') is True:
        decoded['messageKey'] = message.message_key
    if message.description and kwargs.get('incl_desc') is True:
        decoded['description'] = message.description
    decoded['value'], _ = decode_fields(message, buffer, offset)
    if isinstance(coap_message, aiocoap.Message):
        coap_options = {}
        for opt in coap_message.opt.option_list():
            try:
                number = getattr(opt, 'number')
                value = getattr(opt, 'value')
                coap_options[int(number)] = value
            except (AttributeError):
                _log.warning('Error parsing CoAP option')
        if coap_options:
            decoded['coapOptions'] = coap_options
    return decoded


def encode_message(content: dict, **kwargs) -> bytes|aiocoap.Message:
    """Encodes message content using a message definition.
    
    The data bytes produced will be appended to either the first two bytes of
    Non-IP over-the-air data or as the CoAP MessageID (3rd-4th bytes).
    If using the `coap` flag, the output will be a `aiocoap.Message` allowing
    the caller to apply any necessary overhead before final encoding.
    
    Args:
        content (dict): The message content data structure.
        **messages (Messages): The messages codec list to use for encoding.
            Must be present if not using `message`.
        **message (Message): The message codec to use for encoding.
            Must be present if notusing `messages`.
        **nim (bool): Include the message_key as the first 2 bytes for transport.
        **coap (bool): Create a CoAP message using message_key as MessageID
    
    Returns:
        bytes: The data buffer for payload (without message_key header bytes)
    """
    req_keys = ['name', 'value']
    if not isinstance(content, dict) or not all(k in content for k in req_keys):
        raise ValueError(f'Content missing keys ({req_keys})')
    if not isinstance(content['value'], dict):
        raise ValueError('Invalid content value.')
    messages = kwargs.get('messages')
    message = kwargs.get('message')
    nim = kwargs.get('nim') is True
    coap = kwargs.get('coap') is True
    if messages and not isinstance(messages, Messages):
        raise ValueError('Invalid Messages codec list.')
    if message and not isinstance(message, Message):
        raise ValueError('Invalid Message codec.')
    if not messages and not message:
        raise ValueError('Missing codec list or codec.')
    if not message and messages:
        try:
            message = messages[content['name']]
        except ValueError as exc:
            raise ValueError(f'Codec not found for {content["name"]}') from exc
    assert message is not None
    if content['name'] != message.name:
        raise ValueError('Mismatch content name and Message name')
    buffer = bytearray()
    offset = 0
    if nim:
        if coap:
            raise ValueError('nim and coap are mutually exclusive flags')
        buffer = append_bytes_to_buffer(message.message_key.to_bytes(2, 'big'),
                                        buffer,
                                        offset)
        offset = 16
    if not nim and not coap:
        _log.info('Encoding payload-only (no NIM or CoAP header)')
    buffer, offset = encode_fields(content['value'], message, buffer, offset)
    if coap:
        return aiocoap.Message(mid=message.message_key, payload=bytes(buffer))
    return bytes(buffer)            
