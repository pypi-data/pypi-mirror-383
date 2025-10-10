from __future__ import annotations

import base64
import typing as t
from datetime import datetime, timezone
from pathlib import Path

import pytest

import tests.models as models
import uniserde
import uniserde.type_hint


def test_serialize_exact_variant_1() -> None:
    serde = uniserde.JsonSerde()

    value_fresh = models.TestClass.create_variant_1()

    value_json = serde.as_json(value_fresh)

    assert value_json == {
        "id": 1,
        "val_bool": value_fresh.val_bool,
        "val_int": value_fresh.val_int,
        "val_float": value_fresh.val_float,
        "val_bytes": base64.b64encode(value_fresh.val_bytes).decode("utf-8"),
        "val_str": value_fresh.val_str,
        "val_datetime": value_fresh.val_datetime.isoformat(),
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
        "val_object_id": str(value_fresh.val_object_id),
        "val_literal": value_fresh.val_literal,
        "val_enum": "ONE",
        "val_flag": ["ONE", "TWO"],
        "val_path": str(value_fresh.val_path),
        "val_uuid": str(value_fresh.val_uuid),
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
    serde = uniserde.JsonSerde(lazy=lazy)

    value_fresh = models.TestClass.create_variant_1()

    value_json = serde.as_json(value_fresh)

    value_round_trip = serde.from_json(models.TestClass, value_json)
    assert value_fresh == value_round_trip


@pytest.mark.parametrize("lazy", [False, True])
def test_round_trip_variant_2(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    value_fresh = models.TestClass.create_variant_2()

    value_json = serde.as_json(value_fresh)

    value_round_trip = serde.from_json(models.TestClass, value_json)
    assert value_fresh == value_round_trip


@pytest.mark.parametrize(
    "as_type",
    [
        models.ParentClass,
        None,
    ],
)
def test_serialize_parent(as_type: t.Type[t.Any] | None) -> None:
    serde = uniserde.JsonSerde()

    value_fresh = models.ParentClass.create_parent_variant_1()

    value_json = serde.as_json(value_fresh, as_type=as_type)
    assert value_json == value_fresh.serialized_should()


@pytest.mark.parametrize(
    "as_type",
    [
        models.ChildClass,
        models.ParentClass,
        None,
    ],
)
def test_serialize_child(as_type: t.Type[t.Any] | None) -> None:
    serde = uniserde.JsonSerde()

    value_fresh = models.ChildClass.create_child_variant_1()

    value_json = serde.as_json(value_fresh, as_type=as_type)
    print(f"fresh: {value_fresh}")
    print(f"fresh should: {value_fresh.serialized_should()}")
    assert value_json == value_fresh.serialized_should()


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
    serde = uniserde.JsonSerde(lazy=lazy)

    value_fresh = models.ParentClass.create_parent_variant_1()
    value_json = value_fresh.serialized_should()

    value_deserialized: models.ParentClass = serde.from_json(
        as_type,
        value_json,
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
    serde = uniserde.JsonSerde(lazy=lazy)

    value_fresh = models.ChildClass.create_child_variant_1()
    value_json = value_fresh.serialized_should()

    value_deserialized: models.ChildClass = serde.from_json(as_type, value_json)
    assert isinstance(value_deserialized, models.ChildClass)
    assert value_deserialized.parent_int == value_fresh.parent_int
    assert value_deserialized.parent_float == value_fresh.parent_float
    assert value_deserialized.child_float == value_fresh.child_float
    assert value_deserialized.child_str == value_fresh.child_str


def test_kw_only() -> None:
    serde = uniserde.JsonSerde()

    value_fresh = models.ClassWithKwOnly(1, bar=2)

    value_json = serde.as_json(value_fresh)

    assert isinstance(value_json, dict)
    assert "foo" in value_json
    assert "bar" in value_json
    assert "_" not in value_json
    assert len(value_json) == 2
    assert value_json["foo"] == 1
    assert value_json["bar"] == 2


@pytest.mark.parametrize("lazy", [False, True])
def test_dataclass_with_defaults(lazy: bool) -> None:
    """Test that dataclass default values work correctly."""
    serde = uniserde.JsonSerde(lazy=lazy)

    # Create instance with defaults
    value = models.WithDefaults(required=10)
    assert value.optional_value == 42
    assert value.optional_factory == []

    # Serialize and deserialize
    json_value = serde.as_json(value)
    result = serde.from_json(models.WithDefaults, json_value)

    assert result.required == 10
    assert result.optional_value == 42
    assert result.optional_factory == []


def test_dataclass_defaults_overridden_eager() -> None:
    """Test that explicitly set values override defaults (eager mode)."""
    serde = uniserde.JsonSerde(lazy=False)

    value = models.WithDefaults(
        required=10, optional_value=99, optional_factory=[1, 2, 3]
    )
    json_value = serde.as_json(value)
    result = serde.from_json(models.WithDefaults, json_value)

    assert result.required == 10
    assert result.optional_value == 99
    assert result.optional_factory == [1, 2, 3]


def test_dataclass_defaults_overridden_lazy() -> None:
    """Test that explicitly set values override defaults (lazy mode)."""
    serde = uniserde.JsonSerde(lazy=True)

    value = models.WithDefaults(
        required=10, optional_value=99, optional_factory=[1, 2, 3]
    )
    json_value = serde.as_json(value)
    result = serde.from_json(models.WithDefaults, json_value)

    assert result.required == 10
    assert result.optional_value == 99
    assert result.optional_factory == [1, 2, 3]


@pytest.mark.parametrize("lazy", [False, True])
def test_datetime_parses_timezone(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    value_parsed = serde.from_json(datetime, "2020-01-01T01:02:03.000004Z")

    assert isinstance(value_parsed, datetime)
    assert value_parsed.tzinfo is not None
    assert value_parsed == datetime(2020, 1, 1, 1, 2, 3, 4, timezone.utc)


@pytest.mark.parametrize("lazy", [False, True])
def test_int_is_float(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    serde.from_json(float, 1)


@pytest.mark.parametrize("lazy", [False, True])
def test_paths_are_made_absolute(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    path_relative = Path.home() / "folder"
    path_relative = path_relative.relative_to(Path.home())
    assert not path_relative.is_absolute()

    path_absolute = path_relative.absolute()
    assert path_absolute.is_absolute()

    path_serialized = serde.as_json(path_relative)
    assert path_serialized == str(path_absolute)

    path_deserialized = serde.from_json(Path, path_serialized)
    assert path_deserialized == path_absolute


def test_overridden_as_json() -> None:
    serde = uniserde.JsonSerde()

    value_fresh = models.ClassWithStaticmethodOverrides.create()

    value_json = serde.as_json(value_fresh)

    assert value_json == {
        "value": "overridden during serialization",
        "format": "json",
    }


@pytest.mark.parametrize("lazy", [False, True])
def test_overridden_from_json_staticmethod(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    value_json = {
        "value": "stored value",
        "format": "json",
    }

    value_parsed = serde.from_json(models.ClassWithStaticmethodOverrides, value_json)

    assert isinstance(value_parsed, models.ClassWithStaticmethodOverrides)
    assert value_parsed.value == "overridden during deserialization"
    assert value_parsed.format == "json"


@pytest.mark.parametrize("lazy", [False, True])
def test_overridden_from_json_classmethod(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    value_json = {
        "value": "stored value",
        "format": "json",
    }

    value_parsed = serde.from_json(models.ClassWithClassmethodOverrides, value_json)

    assert isinstance(value_parsed, models.ClassWithClassmethodOverrides)
    assert value_parsed.value == "overridden during deserialization"
    assert value_parsed.format == "json"


def test_serialize_with_custom_handlers() -> None:
    """
    Provides custom handlers for some types during serialization.
    """
    serde = uniserde.JsonSerde(
        custom_serializers={
            int: lambda serde, val, as_type: val + 1,
        },
    )

    value_fresh = models.SimpleClass(1, "one")

    value_json = serde.as_json(value_fresh)

    assert value_json == {
        "foo": 2,
        "bar": "one",
    }


@pytest.mark.parametrize("lazy", [False, True])
def test_deserialize_with_custom_handlers(lazy: bool) -> None:
    """
    Provides custom handlers for some types during deserialization.
    """
    serde = uniserde.JsonSerde(
        lazy=lazy,
        custom_deserializers={
            int: lambda serde, val, as_type: val + 1,
        },
    )

    value_json = {
        "foo": 1,
        "bar": "one",
    }

    value_parsed = serde.from_json(models.SimpleClass, value_json)

    assert value_parsed == models.SimpleClass(2, "one")


def test_is_not_lazy_if_not_requested() -> None:
    """
    Make sure that when asking for eager deserialization, we get eager
    deserialization.
    """
    serde = uniserde.JsonSerde(lazy=False)

    value_fresh = models.TestClass.create_variant_1()
    value_json = serde.as_json(value_fresh)
    value_parsed = serde.from_json(models.TestClass, value_json)

    assert "_uniserde_remaining_fields_" not in vars(value_parsed)


def test_is_lazy_if_requested() -> None:
    """
    Make sure that when asking for eager deserialization, we get eager
    deserialization.
    """
    serde = uniserde.JsonSerde(lazy=True)

    value_fresh = models.TestClass.create_variant_1()
    value_json = serde.as_json(value_fresh)
    value_parsed = serde.from_json(models.TestClass, value_json)

    assert "_uniserde_remaining_fields_" in vars(value_parsed)


@pytest.mark.parametrize("lazy", [False, True])
def test_overcaching(lazy: bool) -> None:
    """
    The serde caches handlers for types. If not careful, this could lead to e.g.
    `list[int]` and `list[str]` being cached as the same handler. This test
    makes sure that this does not happen.
    """
    serde = uniserde.JsonSerde(lazy=lazy)

    int_list_fresh = [1, 2, 3]
    str_list_fresh = ["one", "two", "three"]

    int_list_json = serde.as_json(int_list_fresh, as_type=list[int])
    assert int_list_json == [1, 2, 3]

    str_list_json = serde.as_json(str_list_fresh, as_type=list[str])
    assert str_list_json == ["one", "two", "three"]

    int_list_parsed = serde.from_json(list[int], int_list_json)
    assert int_list_parsed == [1, 2, 3]

    str_list_parsed = serde.from_json(list[str], str_list_json)
    assert str_list_parsed == ["one", "two", "three"]
