from __future__ import annotations

import typing as t
from datetime import datetime, timezone

import pytest

import tests.models as models
import uniserde


def test_serialize_exact_variant_1() -> None:
    value_fresh = models.TestClass.create_variant_1()

    serde = uniserde.BsonSerde()
    value_bson = serde.as_bson(value_fresh)

    assert value_bson == {
        "id": 1,
        "val_bool": value_fresh.val_bool,
        "val_int": value_fresh.val_int,
        "val_float": value_fresh.val_float,
        "val_bytes": value_fresh.val_bytes,
        "val_str": value_fresh.val_str,
        "val_datetime": value_fresh.val_datetime,
        "val_timedelta": value_fresh.val_timedelta.total_seconds(),
        "val_tuple": list(value_fresh.val_tuple),
        "val_list": value_fresh.val_list,
        "val_set": list(value_fresh.val_set),
        "val_dict": value_fresh.val_dict,
        "val_optional": value_fresh.val_optional,
        "val_old_union_optional_1": value_fresh.val_old_union_optional_1,
        "val_old_union_optional_2": value_fresh.val_old_union_optional_2,
        "val_new_union_optional_1": value_fresh.val_new_union_optional_1,
        "val_new_union_optional_2": value_fresh.val_new_union_optional_2,
        "val_any": value_fresh.val_any,
        "val_object_id": value_fresh.val_object_id,
        "val_literal": value_fresh.val_literal,
        "val_enum": "ONE",
        "val_flag": ["ONE", "TWO"],
        "val_path": str(value_fresh.val_path),
        "val_uuid": value_fresh.val_uuid,
        "val_class": {
            "foo": value_fresh.val_class.foo,
            "bar": value_fresh.val_class.bar,
        },
        "val_annotated": value_fresh.val_annotated,
        "val_annotated_nested": value_fresh.val_annotated_nested,
        "val_annotated_generic": value_fresh.val_annotated_generic,
        "val_literal_te": value_fresh.val_literal_te,
        "val_optional_te": value_fresh.val_optional_te,
        "val_union_optional_te": value_fresh.val_union_optional_te,
        "val_any_te": value_fresh.val_any_te,
        "val_annotated_te": value_fresh.val_annotated_te,
        "val_annotated_nested_te": value_fresh.val_annotated_nested_te,
        "val_annotated_generic_te": value_fresh.val_annotated_generic_te,
        "val_list_literal_te": value_fresh.val_list_literal_te,
    }


@pytest.mark.parametrize("lazy", [False, True])
def test_round_trip_variant_1(lazy: bool) -> None:
    serde = uniserde.BsonSerde(lazy=lazy)

    value_fresh = models.TestClass.create_variant_1()

    value_bson = serde.as_bson(value_fresh)

    value_round_trip = serde.from_bson(models.TestClass, value_bson)

    assert value_fresh == value_round_trip


@pytest.mark.parametrize("lazy", [False, True])
def test_round_trip_variant_2(lazy: bool) -> None:
    serde = uniserde.BsonSerde(lazy=lazy)

    value_fresh = models.TestClass.create_variant_2()

    value_bson = serde.as_bson(value_fresh)

    value_round_trip = serde.from_bson(models.TestClass, value_bson)

    assert value_fresh == value_round_trip


@pytest.mark.parametrize(
    "as_type",
    [
        models.ParentClass,
        None,
    ],
)
def test_serialize_parent(as_type: t.Type[t.Any] | None) -> None:
    serde = uniserde.BsonSerde()

    value_fresh = models.ParentClass.create_parent_variant_1()

    value_bson = serde.as_bson(value_fresh, as_type=as_type)
    assert value_bson == value_fresh.serialized_should()


@pytest.mark.parametrize(
    "as_type",
    [
        models.ChildClass,
        models.ParentClass,
        None,
    ],
)
def test_serialize_child(as_type: t.Type[t.Any] | None) -> None:
    serde = uniserde.BsonSerde()

    value_fresh = models.ChildClass.create_child_variant_1()

    value_bson = serde.as_bson(value_fresh, as_type=as_type)
    assert value_bson == value_fresh.serialized_should()


@pytest.mark.parametrize(
    "as_type",
    [
        models.ParentClass,
        models.ChildClass,
    ],
)
@pytest.mark.parametrize(
    "lazy",
    [False, True],
)
def test_deserialize_parent(as_type: t.Type[t.Any], lazy: bool) -> None:
    serde = uniserde.BsonSerde(lazy=lazy)

    value_fresh = models.ParentClass.create_parent_variant_1()
    value_bson = value_fresh.serialized_should()

    value_deserialized: models.ParentClass = serde.from_bson(
        as_type,
        value_bson,
    )
    assert isinstance(value_deserialized, models.ParentClass)
    assert value_deserialized.parent_int == value_fresh.parent_int
    assert value_deserialized.parent_float == value_fresh.parent_float


@pytest.mark.parametrize(
    "as_type",
    [
        models.ParentClass,
        models.ChildClass,
    ],
)
@pytest.mark.parametrize(
    "lazy",
    [False, True],
)
def test_deserialize_child(as_type: t.Type[t.Any], lazy: bool) -> None:
    serde = uniserde.BsonSerde(lazy=lazy)

    value_fresh = models.ChildClass.create_child_variant_1()
    value_bson = value_fresh.serialized_should()

    value_deserialized: models.ChildClass = serde.from_bson(as_type, value_bson)
    assert isinstance(value_deserialized, models.ChildClass)
    assert value_deserialized.parent_int == value_fresh.parent_int
    assert value_deserialized.parent_float == value_fresh.parent_float
    assert value_deserialized.child_float == value_fresh.child_float
    assert value_deserialized.child_str == value_fresh.child_str


def test_kw_only() -> None:
    serde = uniserde.BsonSerde()

    value_fresh = models.ClassWithKwOnly(1, bar=2)

    value_bson = serde.as_bson(value_fresh)

    assert isinstance(value_bson, dict)
    assert "foo" in value_bson
    assert "bar" in value_bson
    assert "_" not in value_bson
    assert len(value_bson) == 2
    assert value_bson["foo"] == 1
    assert value_bson["bar"] == 2


@pytest.mark.parametrize("lazy", [False, True])
def test_dataclass_with_defaults(lazy: bool) -> None:
    """Test that dataclass default values work correctly."""
    serde = uniserde.BsonSerde(lazy=lazy)

    # Create instance with defaults
    value = models.WithDefaults(required=10)
    assert value.optional_value == 42
    assert value.optional_factory == []

    # Serialize and deserialize
    bson_value = serde.as_bson(value)
    result = serde.from_bson(models.WithDefaults, bson_value)

    assert result.required == 10
    assert result.optional_value == 42
    assert result.optional_factory == []


def test_dataclass_defaults_overridden_eager() -> None:
    """Test that explicitly set values override defaults (eager mode)."""
    serde = uniserde.BsonSerde(lazy=False)

    value = models.WithDefaults(
        required=10, optional_value=99, optional_factory=[1, 2, 3]
    )
    bson_value = serde.as_bson(value)
    result = serde.from_bson(models.WithDefaults, bson_value)

    assert result.required == 10
    assert result.optional_value == 99
    assert result.optional_factory == [1, 2, 3]


def test_dataclass_defaults_overridden_lazy() -> None:
    """Test that explicitly set values override defaults (lazy mode)."""
    serde = uniserde.BsonSerde(lazy=True)

    value = models.WithDefaults(
        required=10, optional_value=99, optional_factory=[1, 2, 3]
    )
    bson_value = serde.as_bson(value)
    result = serde.from_bson(models.WithDefaults, bson_value)

    assert result.required == 10
    assert result.optional_value == 99
    assert result.optional_factory == [1, 2, 3]


@pytest.mark.parametrize("lazy", [False, True])
def test_datetime_imputes_timezone(lazy: bool) -> None:
    # MongoDB does not explicitly store timezone information, but rather
    # converts everything to UTC. Make sure uniserde understands this and
    # imputes UTC.
    serde = uniserde.BsonSerde(lazy=lazy)

    value_parsed = serde.from_bson(
        datetime,
        datetime(2020, 1, 1, 1, 2, 3, 4),
    )

    assert isinstance(value_parsed, datetime)
    assert value_parsed.tzinfo is not None
    assert value_parsed == datetime(2020, 1, 1, 1, 2, 3, 4, timezone.utc)


def test_int_is_float() -> None:
    serde = uniserde.BsonSerde()

    serde.from_bson(float, 1)


def test_overridden_as_bson() -> None:
    serde = uniserde.BsonSerde()

    value_fresh = models.ClassWithStaticmethodOverrides.create()

    value_bson = serde.as_bson(value_fresh)

    assert value_bson == {
        "value": "overridden during serialization",
        "format": "bson",
    }


@pytest.mark.parametrize("lazy", [False, True])
def test_overridden_from_bson_staticmethod(lazy: bool) -> None:
    serde = uniserde.BsonSerde(lazy=lazy)

    value_bson = {
        "value": "stored value",
        "format": "bson",
    }

    value_parsed = serde.from_bson(
        models.ClassWithStaticmethodOverrides,
        value_bson,
    )

    assert isinstance(value_parsed, models.ClassWithStaticmethodOverrides)
    assert value_parsed.value == "overridden during deserialization"
    assert value_parsed.format == "bson"


@pytest.mark.parametrize("lazy", [False, True])
def test_overridden_from_bson_classmethod(lazy: bool) -> None:
    serde = uniserde.BsonSerde(lazy=lazy)

    value_bson = {
        "value": "stored value",
        "format": "bson",
    }

    value_parsed = serde.from_bson(
        models.ClassWithClassmethodOverrides,
        value_bson,
    )

    assert isinstance(value_parsed, models.ClassWithClassmethodOverrides)
    assert value_parsed.value == "overridden during deserialization"
    assert value_parsed.format == "bson"


def test_serialize_with_custom_handlers() -> None:
    """
    Provides custom handlers for some types during serialization.
    """
    serde = uniserde.BsonSerde(
        custom_serializers={
            int: lambda serde, val, as_type: val + 1,
        }
    )

    value_fresh = models.SimpleClass(1, "one")

    value_bson = serde.as_bson(value_fresh, as_type=models.SimpleClass)

    assert value_bson == {
        "foo": 2,
        "bar": "one",
    }


@pytest.mark.parametrize("lazy", [False, True])
def test_deserialize_with_custom_handlers(lazy: bool) -> None:
    """
    Provides custom handlers for some types during deserialization.
    """
    serde = uniserde.BsonSerde(
        custom_deserializers={
            int: lambda serde, val, as_type: val + 1,
        },
        lazy=lazy,
    )

    value_bson = {
        "foo": 1,
        "bar": "one",
    }

    value_parsed = serde.from_bson(
        models.SimpleClass,
        value_bson,
    )

    assert value_parsed == models.SimpleClass(2, "one")


def test_is_not_lazy_if_not_requested() -> None:
    """
    Make sure that when asking for eager deserialization, we get eager
    deserialization.
    """
    serde = uniserde.BsonSerde(lazy=False)

    value_fresh = models.TestClass.create_variant_1()

    value_bson = serde.as_bson(value_fresh)

    value_parsed = serde.from_bson(models.TestClass, value_bson)

    assert "_uniserde_remaining_fields_" not in vars(value_parsed)


def test_is_lazy_if_requested() -> None:
    """
    Make sure that when asking for eager deserialization, we get eager
    deserialization.
    """
    serde = uniserde.BsonSerde(lazy=True)

    value_fresh = models.TestClass.create_variant_1()

    value_bson = serde.as_bson(value_fresh)

    value_parsed = serde.from_bson(models.TestClass, value_bson)

    assert "_uniserde_remaining_fields_" in vars(value_parsed)


@pytest.mark.parametrize("lazy", [False, True])
def test_overcaching(lazy: bool) -> None:
    """
    The serde caches handlers for types. If not careful, this could lead to e.g.
    `list[int]` and `list[str]` being cached as the same handler. This test
    makes sure that this does not happen.
    """
    serde = uniserde.BsonSerde(lazy=lazy)

    int_list_fresh = [1, 2, 3]
    str_list_fresh = ["one", "two", "three"]

    int_list_bson = serde.as_bson(int_list_fresh, as_type=list[int])
    assert int_list_bson == [1, 2, 3]

    str_list_bson = serde.as_bson(str_list_fresh, as_type=list[str])
    assert str_list_bson == ["one", "two", "three"]

    int_list_parsed = serde.from_bson(list[int], int_list_bson)
    assert int_list_parsed == [1, 2, 3]

    str_list_parsed = serde.from_bson(list[str], str_list_bson)
    assert str_list_parsed == ["one", "two", "three"]
