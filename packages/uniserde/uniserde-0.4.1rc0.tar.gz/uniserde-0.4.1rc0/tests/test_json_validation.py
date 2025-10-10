"""
Error handling and validation tests for JSON serialization.

Tests that uniserde fails gracefully with clear error messages when given
invalid inputs, malformed data, or unsupported type structures.
"""

from __future__ import annotations

import uuid
from datetime import datetime

import pytest

import tests.models as models
import uniserde


@pytest.mark.parametrize("lazy", [False, True])
def test_wrong_nested_type_in_list(lazy: bool) -> None:
    """Test that wrong types in lists are caught."""
    serde = uniserde.JsonSerde(lazy=lazy)

    with pytest.raises(uniserde.SerdeError):
        serde.from_json(list[int], ["not", "integers"])


@pytest.mark.parametrize("lazy", [False, True])
def test_wrong_nested_type_in_dict(lazy: bool) -> None:
    """Test that wrong types in dict values are caught."""
    serde = uniserde.JsonSerde(lazy=lazy)

    with pytest.raises(uniserde.SerdeError):
        serde.from_json(dict[str, int], {"key": "not_int"})


@pytest.mark.parametrize("lazy", [False, True])
def test_invalid_base64(lazy: bool) -> None:
    """Test that invalid base64 strings are caught."""
    serde = uniserde.JsonSerde(lazy=lazy)

    with pytest.raises(uniserde.SerdeError, match="invalid base64"):
        serde.from_json(bytes, "not-valid-base64!!!")


@pytest.mark.parametrize("lazy", [False, True])
def test_invalid_datetime(lazy: bool) -> None:
    """Test that invalid datetime strings are caught."""
    serde = uniserde.JsonSerde(lazy=lazy)

    with pytest.raises(uniserde.SerdeError, match="Invalid date/time"):
        serde.from_json(datetime, "not-a-date")


@pytest.mark.parametrize("lazy", [False, True])
def test_invalid_uuid(lazy: bool) -> None:
    """Test that invalid UUID strings are caught."""
    serde = uniserde.JsonSerde(lazy=lazy)

    with pytest.raises(uniserde.SerdeError, match="Invalid UUID"):
        serde.from_json(uuid.UUID, "not-a-uuid")


@pytest.mark.parametrize("lazy", [False, True])
def test_tuple_wrong_length_too_many(lazy: bool) -> None:
    """Test that tuples with too many elements are caught."""
    serde = uniserde.JsonSerde(lazy=lazy)

    with pytest.raises(uniserde.SerdeError, match="Expected list of length"):
        serde.from_json(tuple[int, str], [1, "two", "three"])


@pytest.mark.parametrize("lazy", [False, True])
def test_tuple_wrong_length_too_few(lazy: bool) -> None:
    """Test that tuples with too few elements are caught."""
    serde = uniserde.JsonSerde(lazy=lazy)

    with pytest.raises(uniserde.SerdeError, match="Expected list of length"):
        serde.from_json(tuple[int, str], [1])


@pytest.mark.parametrize("lazy", [False, True])
def test_tuple_wrong_element_types(lazy: bool) -> None:
    """Test that tuples with wrong element types are caught."""
    serde = uniserde.JsonSerde(lazy=lazy)

    with pytest.raises(uniserde.SerdeError):
        serde.from_json(tuple[int, str], ["wrong", 123])


# NOTE: Recursive types are NOT supported by uniserde and will raise
# a clear SerdeError. These tests verify that the error message is helpful.


@pytest.mark.parametrize("lazy", [False, True])
def test_forward_reference_simple(lazy: bool) -> None:
    """Test that recursive types are detected and rejected with a clear error."""
    serde = uniserde.JsonSerde(lazy=lazy)

    # Create a simple tree
    leaf1 = models.TreeNode(value=1)
    leaf2 = models.TreeNode(value=2)
    root = models.TreeNode(value=0, children=[leaf1, leaf2])

    # Should raise a clear error about recursive types
    with pytest.raises(uniserde.SerdeError, match="Recursive type detected"):
        serde.as_json(root)


@pytest.mark.parametrize("lazy", [False, True])
def test_forward_reference_nested(lazy: bool) -> None:
    """Test that deeply nested recursive types are also detected."""
    serde = uniserde.JsonSerde(lazy=lazy)

    # Create a deeper tree
    leaf = models.TreeNode(value=3)
    middle = models.TreeNode(value=2, children=[leaf])
    root = models.TreeNode(value=1, children=[middle])

    # Should raise a clear error about recursive types
    with pytest.raises(uniserde.SerdeError, match="Recursive type detected"):
        serde.as_json(root)


@pytest.mark.parametrize("lazy", [False, True])
def test_dict_int_keys_invalid(lazy: bool) -> None:
    """Test that invalid int keys are caught."""
    serde = uniserde.JsonSerde(lazy=lazy)

    with pytest.raises(uniserde.SerdeError, match="Invalid key"):
        serde.from_json(dict[int, str], {"not_an_int": "value"})


@pytest.mark.parametrize("lazy", [False, True])
def test_type_mismatch_int_expected_str_given(lazy: bool) -> None:
    """Test error when expecting int but getting string."""
    serde = uniserde.JsonSerde(lazy=lazy)

    with pytest.raises(uniserde.SerdeError, match="Expected int"):
        serde.from_json(int, "not an int")


@pytest.mark.parametrize("lazy", [False, True])
def test_type_mismatch_list_expected_dict_given(lazy: bool) -> None:
    """Test error when expecting list but getting dict."""
    serde = uniserde.JsonSerde(lazy=lazy)

    with pytest.raises(uniserde.SerdeError, match="Expected list"):
        serde.from_json(list[int], {"key": "value"})


@pytest.mark.parametrize("lazy", [False, True])
def test_type_mismatch_dict_expected_list_given(lazy: bool) -> None:
    """Test error when expecting dict but getting list."""
    serde = uniserde.JsonSerde(lazy=lazy)

    with pytest.raises(uniserde.SerdeError, match="Expected dict"):
        serde.from_json(dict[str, int], [1, 2, 3])


@pytest.mark.parametrize("lazy", [False, True])
def test_datetime_needs_timezone(lazy: bool) -> None:
    """Test that datetime strings without timezone are rejected."""
    serde = uniserde.JsonSerde(lazy=lazy)

    with pytest.raises(uniserde.SerdeError, match="is missing a timezone."):
        serde.from_json(datetime, "2020-01-01T01:02:03.000004")


def test_catch_superfluous_value() -> None:
    """Test that extra fields in JSON objects are caught."""
    serde = uniserde.JsonSerde()

    with pytest.raises(uniserde.SerdeError, match="Object contains superfluous fields"):
        serde.from_json(
            models.SimpleClass,
            {
                "foo": 1,
                "bar": "one",
                "invalidKey": True,
            },
        )
