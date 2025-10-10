from __future__ import annotations

import pytest

import tests.models as models
import uniserde
import uniserde.lazy_wrapper


def test_lazy_only_eagerly_deserializes_fields_with_class_attributes() -> None:
    """Verify that ONLY fields with class attributes are eagerly deserialized."""
    serde = uniserde.JsonSerde(lazy=True)

    value = models.WithDefaults(
        required=10, optional_value=99, optional_factory=[1, 2, 3]
    )
    json_value = serde.as_json(value)
    result = serde.from_json(models.WithDefaults, json_value)

    # Check what's in the instance __dict__ vs remaining fields
    instance_dict = {
        k: v for k, v in vars(result).items() if not k.startswith("_uniserde")
    }
    remaining = getattr(result, "_uniserde_remaining_fields_", {})

    # Fields WITH class attributes (default=value) should be eagerly deserialized
    assert (
        "optional_value" in instance_dict
    ), "Field with class attribute should be eagerly deserialized"

    # Fields WITHOUT class attributes should remain lazy:
    # - required (no default at all)
    # - optional_factory (default_factory doesn't create class attribute)
    assert "required" not in instance_dict, "Field without default should remain lazy"
    assert (
        "optional_factory" not in instance_dict
    ), "Field with default_factory should remain lazy"

    assert (
        "required" in remaining
    ), "Field without default should be in remaining_fields"
    assert (
        "optional_factory" in remaining
    ), "Field with default_factory should be in remaining_fields"


def test_lazy_field_without_default_is_truly_lazy() -> None:
    """Verify that fields without defaults are not deserialized until accessed."""
    serde = uniserde.JsonSerde(lazy=True)

    value = models.WithDefaults(
        required=10, optional_value=99, optional_factory=[1, 2, 3]
    )
    json_value = serde.as_json(value)
    result = serde.from_json(models.WithDefaults, json_value)

    # Before accessing 'required', it should NOT be deserialized
    remaining_before = result._uniserde_remaining_fields_.copy()
    assert "required" in remaining_before, "Field should be in remaining before access"

    # Access the field
    value = result.required
    assert value == 10

    # After accessing, it should be deserialized and removed from remaining
    remaining_after = result._uniserde_remaining_fields_
    assert (
        "required" not in remaining_after
    ), "Field should be removed from remaining after access"
    assert "required" in vars(result), "Field should now be in instance __dict__"


def test_lazy_class_with_no_defaults_is_fully_lazy() -> None:
    """Verify that classes with NO defaults remain fully lazy."""
    serde = uniserde.JsonSerde(lazy=True)

    # SimpleClass has no defaults at all
    value = models.SimpleClass(foo=42, bar="hello")
    json_value = serde.as_json(value)
    result = serde.from_json(models.SimpleClass, json_value)

    # Check that nothing was eagerly deserialized
    instance_dict = {
        k: v for k, v in vars(result).items() if not k.startswith("_uniserde")
    }
    assert (
        len(instance_dict) == 0
    ), "No fields should be eagerly deserialized when there are no defaults"

    # All fields should be in remaining
    remaining = result._uniserde_remaining_fields_
    assert "foo" in remaining, "All fields should be in remaining_fields"
    assert "bar" in remaining, "All fields should be in remaining_fields"

    # Access fields and verify they get deserialized on demand
    assert result.foo == 42
    assert result.bar == "hello"
    assert "foo" in vars(result), "Accessed field should now be in __dict__"
    assert "bar" in vars(result), "Accessed field should now be in __dict__"


def test_dataclass_defaults_overridden_lazy() -> None:
    """Test that explicitly set values override defaults (lazy mode)."""
    serde = uniserde.JsonSerde(lazy=True)

    value = models.WithDefaults(
        required=10, optional_value=99, optional_factory=[1, 2, 3]
    )
    json_value = serde.as_json(value)
    result = serde.from_json(models.WithDefaults, json_value)

    assert result.required == 10
    assert result.optional_value == 99  # Fixed: hybrid eager/lazy approach
    assert result.optional_factory == [1, 2, 3]


def test_missing_attribute_raises_attribute_error() -> None:
    serde = uniserde.JsonSerde(lazy=True)

    # Create a non-lazy instance
    value_eager = models.TestClass.create_variant_1()

    # Create a lazy instance of the same class
    value_lazy = serde.from_json(
        models.TestClass,
        serde.as_json(value_eager),
    )

    assert type(value_eager).__getattr__ is uniserde.lazy_wrapper._lazy_getattr  # type: ignore

    # This has modified the class' `__getattr__` method. Now test that accessing
    # an invalid attribute in fact raises an `AttributeError`, rather than just
    # failing, e.g. because the class is missing some fields expected to be
    # contained in lazy instances.
    with pytest.raises(AttributeError):
        value_lazy.this_is_an_invalid_attribute_name  # type: ignore
