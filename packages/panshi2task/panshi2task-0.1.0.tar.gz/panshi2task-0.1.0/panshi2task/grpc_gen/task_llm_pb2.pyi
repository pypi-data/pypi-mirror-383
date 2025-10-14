from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EntityMiniingRequest(_message.Message):
    __slots__ = ("schema", "text")
    class SchemaItem(_message.Message):
        __slots__ = ("name", "desc")
        NAME_FIELD_NUMBER: _ClassVar[int]
        DESC_FIELD_NUMBER: _ClassVar[int]
        name: str
        desc: str
        def __init__(self, name: _Optional[str] = ..., desc: _Optional[str] = ...) -> None: ...
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    schema: _containers.RepeatedCompositeFieldContainer[EntityMiniingRequest.SchemaItem]
    text: str
    def __init__(self, schema: _Optional[_Iterable[_Union[EntityMiniingRequest.SchemaItem, _Mapping]]] = ..., text: _Optional[str] = ...) -> None: ...

class EntityMiniingResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _struct_pb2.ListValue
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.ListValue, _Mapping]] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: _containers.MessageMap[str, _struct_pb2.ListValue]
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[_Mapping[str, _struct_pb2.ListValue]] = ...) -> None: ...

class FAQMiniingRequest(_message.Message):
    __slots__ = ("text", "except_num")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    EXCEPT_NUM_FIELD_NUMBER: _ClassVar[int]
    text: str
    except_num: int
    def __init__(self, text: _Optional[str] = ..., except_num: _Optional[int] = ...) -> None: ...

class FAQMiniingResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    class QAItem(_message.Message):
        __slots__ = ("query", "answer")
        QUERY_FIELD_NUMBER: _ClassVar[int]
        ANSWER_FIELD_NUMBER: _ClassVar[int]
        query: str
        answer: str
        def __init__(self, query: _Optional[str] = ..., answer: _Optional[str] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: _containers.RepeatedCompositeFieldContainer[FAQMiniingResponse.QAItem]
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[_Iterable[_Union[FAQMiniingResponse.QAItem, _Mapping]]] = ...) -> None: ...

class QuestionGenRequest(_message.Message):
    __slots__ = ("text", "except_num")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    EXCEPT_NUM_FIELD_NUMBER: _ClassVar[int]
    text: str
    except_num: int
    def __init__(self, text: _Optional[str] = ..., except_num: _Optional[int] = ...) -> None: ...

class QuestionGenResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[_Iterable[str]] = ...) -> None: ...

class SummaryRequest(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class SummaryResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: str
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[str] = ...) -> None: ...

class TopicMiningRequest(_message.Message):
    __slots__ = ("titles", "summary")
    TITLES_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    titles: _containers.RepeatedScalarFieldContainer[str]
    summary: str
    def __init__(self, titles: _Optional[_Iterable[str]] = ..., summary: _Optional[str] = ...) -> None: ...

class TopicMiningResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[_Iterable[str]] = ...) -> None: ...
