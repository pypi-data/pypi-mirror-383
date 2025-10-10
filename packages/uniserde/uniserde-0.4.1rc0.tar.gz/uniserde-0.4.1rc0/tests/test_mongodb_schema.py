from __future__ import annotations

import typing as t
import warnings

import pytest

import tests.models as models
import uniserde

# This throws a warning since 3.11, which shows up rather confusingly in pytest.
# Suppress it. (The warning is caused by `mongo_schema`, not uniserde.)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import mongo_schema

try:
    import bson  # type: ignore
except ImportError:
    bson = None


def get_bson_serde_without_uuid_checks() -> uniserde.BsonSerde:
    """
    `mongo_schema` doesn't consider UUIDs to be valid `binData`. While perfectly
    reasonable, in `pymongo`, UUIDs do result in `binData` when stored in the
    database.

    This function builds a MongoDB schema but disables UUID verification to keep
    `mongo_schema` happy.
    """
    serde = uniserde.BsonSerde()
    serde._mongodb_schema_converter._enable_uuid_verification = False
    return serde


@pytest.mark.skipif(bson is None, reason="`pymongo` is not installed")
@pytest.mark.parametrize(
    "value, py_type",
    [
        (models.TestClass.create_variant_1(), models.TestClass),
        (models.TestClass.create_variant_2(), models.TestClass),
        (models.ParentClass.create_parent_variant_1(), models.ParentClass),
        (models.ChildClass.create_child_variant_1(), models.ChildClass),
        (models.ChildClass.create_child_variant_1(), models.ParentClass),
        (models.ClassWithId.create(), models.ClassWithId),
        (models.ClassWithKwOnly.create(), models.ClassWithKwOnly),
    ],
)
def test_value_matches_schema(value: t.Any, py_type: t.Type) -> None:
    serde = get_bson_serde_without_uuid_checks()

    schema = serde.as_mongodb_schema(py_type)

    bson_value = serde.as_bson(value)

    mongo_schema.validate(bson_value, schema)


def test_overridden_as_mongodb_schema_staticmethod() -> None:
    serde = get_bson_serde_without_uuid_checks()
    value_schema = serde.as_mongodb_schema(models.ClassWithStaticmethodOverrides)

    assert value_schema == {
        "value": "overridden value",
        "format": "mongodb schema",
    }


def test_overridden_as_mongodb_schema_classmethod() -> None:
    serde = get_bson_serde_without_uuid_checks()
    value_schema = serde.as_mongodb_schema(models.ClassWithClassmethodOverrides)

    assert value_schema == {
        "value": "overridden value",
        "format": "mongodb schema",
    }
