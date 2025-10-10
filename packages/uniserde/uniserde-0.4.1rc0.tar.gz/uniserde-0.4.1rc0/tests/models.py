from __future__ import annotations

import enum
import typing as t
import uuid
from dataclasses import KW_ONLY, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

import typing_extensions as te

import uniserde
from uniserde import JsonDoc, ObjectId


class RegularEnum(enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3


class FlagEnum(enum.Flag):
    ONE = 1
    TWO = 2
    FOUR = 4


@dataclass
class SimpleClass:
    foo: int
    bar: str


@dataclass
class WithDefaults:
    """
    A class with default values for some fields.
    """

    required: int
    optional_value: int = 42
    optional_factory: list[int] = field(default_factory=list)


@dataclass
class TreeNode:
    """
    A recursive data structure not supported by uniserde.
    """

    value: int
    children: list[TreeNode] = field(default_factory=list)


@dataclass
class TestClass:
    id: int

    val_bool: bool
    val_int: int
    val_float: float
    val_bytes: bytes
    val_str: str
    val_datetime: datetime
    val_timedelta: timedelta
    val_tuple: tuple[int, str]
    val_list: list[int]
    val_set: set[int]
    val_dict: dict[str, int]
    val_optional: t.Optional[int]
    val_old_union_optional_1: t.Union[int, None]
    val_old_union_optional_2: t.Union[None, int]
    val_new_union_optional_1: int | None
    val_new_union_optional_2: None | int
    val_any: t.Any
    val_object_id: ObjectId
    val_literal: t.Literal["one", "two", "three"]
    val_enum: RegularEnum
    val_flag: FlagEnum
    val_path: Path
    val_uuid: uuid.UUID
    val_class: SimpleClass
    val_annotated: t.Annotated[int, "simple annotated field"]
    val_annotated_nested: t.Annotated[
        t.Annotated[str, "inner metadata"], "outer metadata"
    ]
    val_annotated_generic: t.Annotated[list[int], "annotated list"]

    # Values exported from `typing_extensions` are not always the same instances
    # as those in the `typing` module. They are tested separately here to ensure
    # compatibility.
    val_literal_te: te.Literal["one", "two", "three"]
    val_optional_te: te.Optional[int]
    val_union_optional_te: te.Union[int, None]
    val_any_te: te.Any
    val_annotated_te: te.Annotated[int, "simple annotated field"]
    val_annotated_nested_te: te.Annotated[
        te.Annotated[str, "inner metadata"], "outer metadata"
    ]
    val_annotated_generic_te: te.Annotated[list[int], "annotated list"]
    val_list_literal_te: list[te.Literal["x", "y", "z"]]

    @classmethod
    def create_variant_1(cls) -> TestClass:
        return cls(
            id=1,
            val_bool=True,
            val_int=1,
            val_float=1.0,
            val_bytes=b"these are bytes",
            val_str="this is a string",
            val_datetime=datetime(2020, 1, 2, tzinfo=timezone.utc),
            val_timedelta=timedelta(days=1, seconds=2, microseconds=3),
            val_tuple=(1, "one"),
            val_list=[1, 2, 3],
            val_set={1, 2, 3},
            val_dict={"one": 1, "two": 2},
            val_optional=1,
            val_old_union_optional_1=1,
            val_old_union_optional_2=1,
            val_new_union_optional_1=1,
            val_new_union_optional_2=1,
            val_any="this is an ANY value",
            val_object_id=ObjectId("62bd611fa847c71f1b68fffb"),
            val_literal="one",
            val_enum=RegularEnum.ONE,
            val_flag=FlagEnum.ONE | FlagEnum.TWO,
            val_path=Path.home() / "one",
            val_uuid=uuid.UUID("754a5dbf-e7f3-4cc3-b2d7-9382e586cfd3"),
            val_class=SimpleClass(foo=1, bar="one"),
            val_annotated=42,
            val_annotated_nested="nested string",
            val_annotated_generic=[10, 20, 30],
            val_literal_te="one",
            val_optional_te=1,
            val_union_optional_te=1,
            val_any_te="this is an ANY value from typing_extensions",
            val_annotated_te=42,
            val_annotated_nested_te="nested string",
            val_annotated_generic_te=[10, 20, 30],
            val_list_literal_te=["x", "y"],
        )

    @classmethod
    def create_variant_2(cls) -> TestClass:
        return cls(
            id=2,
            val_bool=False,
            val_int=2,
            val_float=2.0,
            val_bytes=b"these are different bytes",
            val_str="this is another string",
            val_datetime=datetime(2024, 5, 6, tzinfo=timezone.utc),
            val_timedelta=timedelta(days=10, seconds=20, microseconds=30),
            val_tuple=(2, "two"),
            val_list=[4, 5, 6],
            val_set={4, 5, 6},
            val_dict={"three": 3, "four": 4},
            val_optional=None,
            val_old_union_optional_1=None,
            val_old_union_optional_2=None,
            val_new_union_optional_1=None,
            val_new_union_optional_2=None,
            val_any="this is another ANY value",
            val_object_id=ObjectId("62bd6122a847c71f1b68fffc"),
            val_literal="two",
            val_enum=RegularEnum.TWO,
            val_flag=FlagEnum.ONE | FlagEnum.TWO | FlagEnum.FOUR,
            val_path=Path.home() / "two",
            val_uuid=uuid.UUID("0eadbc7e-3418-45a5-b276-53e7d91bb79d"),
            val_class=SimpleClass(foo=2, bar="two"),
            val_annotated=99,
            val_annotated_nested="another nested string",
            val_annotated_generic=[100, 200],
            val_literal_te="two",
            val_optional_te=None,
            val_union_optional_te=None,
            val_any_te="this is another ANY value from typing_extensions",
            val_annotated_te=99,
            val_annotated_nested_te="another nested string",
            val_annotated_generic_te=[100, 200],
            val_list_literal_te=["z"],
        )


@dataclass
@uniserde.as_child
class ParentClass:
    parent_int: int
    parent_float: float

    @classmethod
    def create_parent_variant_1(cls) -> ParentClass:
        return cls(
            parent_int=1,
            parent_float=1.0,
        )

    def serialized_should(self) -> JsonDoc:
        return {
            "type": "ParentClass",
            "parent_int": self.parent_int,
            "parent_float": self.parent_float,
        }


@dataclass
class ChildClass(ParentClass):
    child_float: float
    child_str: str

    @classmethod
    def create_child_variant_1(cls) -> ChildClass:
        return cls(
            parent_int=1,
            parent_float=1.0,
            child_float=1.0,
            child_str="this is a string",
        )

    def serialized_should(self) -> JsonDoc:
        return {
            "type": "ChildClass",
            "parent_int": self.parent_int,
            "parent_float": self.parent_float,
            "child_float": self.child_float,
            "child_str": self.child_str,
        }


@dataclass
class ClassWithId:
    id: int
    foo: int

    @classmethod
    def create(cls) -> ClassWithId:
        return cls(1, 2)


@dataclass
class ClassWithKwOnly:
    foo: int

    _: KW_ONLY

    bar: int

    @classmethod
    def create(cls) -> ClassWithKwOnly:
        return cls(1, bar=2)


@dataclass
class ClassWithStaticmethodOverrides:
    """
    Class which has uniserde's special methods overridden. This allows to check
    that they are called rather than the default.

    All methods are overridden as @staticmethod.
    """

    value: str
    format: str

    @classmethod
    def create(cls) -> ClassWithStaticmethodOverrides:
        return cls("stored value", "python")

    def _uniserde_as_json_(
        self,
        serde: uniserde.JsonSerde,
        as_type: t.Type,
    ) -> uniserde.JsonDoc:
        assert isinstance(serde, uniserde.JsonSerde)
        assert as_type is ClassWithStaticmethodOverrides, as_type

        return {"value": "overridden during serialization", "format": "json"}

    def _uniserde_as_bson_(
        self,
        serde: uniserde.BsonSerde,
        as_type: t.Type,
    ) -> uniserde.BsonDoc:
        assert isinstance(serde, uniserde.BsonSerde)
        assert as_type is ClassWithStaticmethodOverrides

        return {"value": "overridden during serialization", "format": "bson"}

    @staticmethod
    def _uniserde_from_json_(
        document: dict[str, t.Any],
        serde: uniserde.JsonSerde,
        as_type: t.Type,
    ) -> ClassWithStaticmethodOverrides:
        assert isinstance(document, dict)
        assert isinstance(serde, uniserde.JsonSerde)
        assert as_type is ClassWithStaticmethodOverrides

        return ClassWithStaticmethodOverrides(
            "overridden during deserialization", "json"
        )

    @staticmethod
    def _uniserde_from_bson_(
        document: dict[str, t.Any],
        serde: uniserde.BsonSerde,
        as_type: t.Type,
    ) -> ClassWithStaticmethodOverrides:
        assert isinstance(document, dict)
        assert isinstance(serde, uniserde.BsonSerde)
        assert as_type is ClassWithStaticmethodOverrides

        return ClassWithStaticmethodOverrides(
            "overridden during deserialization", "bson"
        )

    @staticmethod
    def _uniserde_as_mongodb_schema_(
        serde: uniserde.BsonSerde,
        as_type: t.Type,
    ) -> t.Any:
        assert isinstance(serde, uniserde.BsonSerde)
        assert as_type is ClassWithStaticmethodOverrides

        return {"value": "overridden value", "format": "mongodb schema"}


@dataclass
class ClassWithClassmethodOverrides:
    """
    Same as the class above, but with the methods overridden as @classmethod.
    """

    value: str
    format: str

    @classmethod
    def create(cls) -> ClassWithClassmethodOverrides:
        return cls("stored value", "python")

    @classmethod
    def _uniserde_from_json_(
        cls,
        document: dict[str, t.Any],
        serde: uniserde.JsonSerde,
        as_type: t.Type,
    ) -> ClassWithClassmethodOverrides:
        assert isinstance(document, dict)
        assert isinstance(serde, uniserde.JsonSerde)
        assert as_type is ClassWithClassmethodOverrides

        return ClassWithClassmethodOverrides(
            "overridden during deserialization", "json"
        )

    @classmethod
    def _uniserde_from_bson_(
        cls,
        document: dict[str, t.Any],
        serde: uniserde.BsonSerde,
        as_type: t.Type,
    ) -> ClassWithClassmethodOverrides:
        assert isinstance(document, dict)
        assert isinstance(serde, uniserde.BsonSerde)
        assert as_type is ClassWithClassmethodOverrides

        return ClassWithClassmethodOverrides(
            "overridden during deserialization", "bson"
        )

    @classmethod
    def _uniserde_as_mongodb_schema_(
        cls,
        serde: uniserde.BsonSerde,
        as_type: t.Type,
    ) -> t.Any:
        assert isinstance(serde, uniserde.BsonSerde)
        assert as_type is ClassWithClassmethodOverrides

        return {"value": "overridden value", "format": "mongodb schema"}
