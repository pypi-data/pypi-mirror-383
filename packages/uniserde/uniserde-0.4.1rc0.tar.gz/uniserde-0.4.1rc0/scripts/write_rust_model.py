"""
Given a uniserde data model, generates the Rust equivalent for it. This assumes
Rust uses the `serde` library for serialization / deserialization. It doesn't
produce perfect code, but the results are typically a good starting point for
writing your own, final version.

The code will be written to `uniserde_models.rs` in the current working
directory.
"""

import enum
import inspect
import typing as t
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import uniserde
import uniserde.case_convert
import uniserde.type_hint
import uniserde.utils
from uniserde.type_hint import TypeHint

PYTHON_TYPES_TO_RUST_TYPES = {
    bool: "bool",
    int: "i32",
    float: "f64",
    str: "String",
    bytes: "Vec<u8>",
    datetime: "DateTime<Utc>",
    timedelta: "Duration",
    uuid.UUID: "Uuid",
}


@dataclass
class SubModel:
    id: str
    timestamp: datetime
    reference_to_other_instance: str
    amount: int
    description: str
    events: list[str]


@dataclass
class Model:
    name: str
    subs: list[SubModel]
    sets: set[str]
    timestamp: datetime
    deleted: bool
    duration: float


def get_all_model_classes(py_type: t.Type) -> t.Iterable[type]:
    """
    Given a model class, returns an iterable over all model classes that must be
    generated.
    """
    as_type = TypeHint(py_type)

    # These types already exist in Rust and need no further processing
    if as_type.origin in {bool, int, float, str, bytes, datetime}:
        return

    # Classes are themselves models, and may contain more
    if inspect.isclass(as_type.origin) and as_type.origin not in {
        tuple,
        list,
        set,
        dict,
    }:
        yield as_type.origin

        for _, attr_as_type in uniserde.utils.get_class_attributes_recursive(
            as_type.origin
        ).items():
            yield from get_all_model_classes(attr_as_type.origin)

    # Recur into the args
    for arg_type in as_type.args:
        yield from get_all_model_classes(arg_type.origin)


def write_rust_struct(
    model: TypeHint,
    out: t.TextIO,
    *,
    public: bool,
) -> None:
    """
    Given a model class, writes the Rust equivalent as a struct.
    """
    assert isinstance(model, TypeHint), model
    assert inspect.isclass(model.origin), model

    out.write("#[derive(Debug, Deserialize)]\n")

    if public:
        out.write("pub ")

    out.write(f"struct {model.origin.__name__} {{\n")

    for ii, (field_name, attr_as_type) in enumerate(
        uniserde.utils.get_class_attributes_recursive(model.origin).items()
    ):
        if ii != 0:
            out.write("\n")

        # Special cases
        if attr_as_type.origin is datetime:
            out.write(f'    #[serde(deserialize_with = "deserialize_iso8601")]\n')
            out.write(f"    {field_name}: DateTime<Utc>,\n")
            continue

        if attr_as_type.origin is timedelta:
            out.write(
                f'    #[serde(deserialize_with = "deserialize_duration_from_seconds")]\n'
            )
            out.write(f"    {field_name}: Duration,\n")
            continue

        # General case
        field_rust_type = convert_type_to_rust(attr_as_type)
        out.write(f"    {field_name}: {field_rust_type},\n")

    out.write("}\n")


def write_rust_enum(
    model: TypeHint,
    out: t.TextIO,
    *,
    public: bool,
) -> None:
    """
    Given an enum class, writes the Rust equivalent as an enum.
    """
    assert issubclass(model.origin, enum.Enum), model

    out.write("#[derive(Debug, Deserialize)]\n")

    if public:
        out.write("pub ")

    out.write(f"enum {model.origin.__name__} {{\n")

    for member in model.origin:
        out.write(f'    #[serde(rename = "{member.name}")]\n')
        out.write(
            f"    {uniserde.case_convert.all_upper_to_upper_camel_case(member.name)},\n\n"
        )

    out.write("}\n")


def write_rust_model(
    model: TypeHint,
    out: t.TextIO,
    *,
    public: bool = True,
) -> None:
    if issubclass(model.origin, enum.Enum):
        write_rust_enum(model, out, public=public)
    else:
        write_rust_struct(model, out, public=public)


def convert_type_to_rust(as_type: TypeHint) -> str:
    """
    Given a Python type, returns the equivalent Rust type.
    """
    # Simple lookups
    try:
        return PYTHON_TYPES_TO_RUST_TYPES[as_type.origin]
    except KeyError:
        pass

    # More complex types
    if as_type.origin is list:
        return f"Vec<{convert_type_to_rust(as_type.args[0])}>"

    if as_type.origin is tuple:
        return f"({', '.join(convert_type_to_rust(arg) for arg in as_type.args)})"

    if as_type.origin is set:
        return f"HashSet<{convert_type_to_rust(as_type.args[0])}>"

    if as_type.origin is dict:
        return f"HashMap<{convert_type_to_rust(as_type.args[0])}, {convert_type_to_rust(as_type.args[1])}>"

    if as_type.origin is t.Optional:
        return f"Option<{convert_type_to_rust(as_type.args[0])}>"

    if inspect.isclass(as_type.origin):
        return as_type.origin.__name__

    raise ValueError(f"Unsupported type: {as_type}")


def write_boilerplate(out: t.TextIO) -> None:
    out.write(
        """
use serde::Deserialize;
use chrono::{DateTime, Duration, Utc};


fn deserialize_iso8601<'de, D>(deserializer: D) -> Result<DateTime<Utc>, D::Error>
where
    D: serde::Deserializer<'de>,
{
    let s: &str = Deserialize::deserialize(deserializer)?;
    DateTime::parse_from_rfc3339(s)
        .map(|dt| dt.with_timezone(&Utc))
        .map_err(serde::de::Error::custom)
}


fn deserialize_duration_from_seconds<'de, D>(deserializer: D) -> Result<Duration, D::Error>
where
    D: serde::Deserializer<'de>,
{
    let seconds: f64 = Deserialize::deserialize(deserializer)?;
    // Convert seconds (float) to chrono::Duration
    Duration::from_std(std::time::Duration::from_secs_f64(seconds))
        .map_err(serde::de::Error::custom)
}
            """.strip()
    )


def main() -> None:
    # Find all models that need porting
    all_model_classes = set(get_all_model_classes(Model))

    with Path("uniserde_models.rs").open("w") as out:
        # Common header code
        write_boilerplate(out)
        out.write("\n\n")

        # Write the Model Code
        for model_cls in all_model_classes:
            write_rust_model(TypeHint(model_cls), out)
            out.write("\n\n")


if __name__ == "__main__":
    main()
