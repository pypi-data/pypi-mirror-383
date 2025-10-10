import typing as t
import uuid
from datetime import datetime, timedelta

import pytest
import typing_extensions as te

from uniserde import ObjectId, type_hint

# Test cases for valid type hints that type_hint.TypeHint should be able to parse. Each
# entry is a 4-tuple:
#
# - raw_type_hint: The actual Python type hint object to parse
# - string_representation: String form of the type hint (used for testing string
#   parsing)
# - expected_origin: The origin that type_hint.TypeHint should extract (e.g., list from
#   list[int])
# - expected_args: Tuple of types that should be extracted as args (e.g., (int,)
#   from list[int])
UNPARSED_VALID_TYPE_HINTS = (
    (bool, "bool", bool, ()),
    (int, "int", int, ()),
    (float, "float", float, ()),
    (str, "str", str, ()),
    (tuple[int], "tuple[int]", tuple, (int,)),
    (list[str], "list[str]", list, (str,)),
    (set[float], "set[float]", set, (float,)),
    (dict[str, int], "dict[str, int]", dict, (str, int)),
    (t.Optional[str], "t.Optional[str]", t.Optional, (str,)),
    (t.Union[str, None], "t.Union[str, None]", t.Optional, (str,)),
    (t.Union[None, str], "t.Union[None, str]", t.Optional, (str,)),
    (datetime, "datetime", datetime, ()),
    (timedelta, "timedelta", timedelta, ()),
    (ObjectId, "ObjectId", ObjectId, ()),
    (uuid.UUID, "uuid.UUID", uuid.UUID, ()),
    (t.Annotated[int, "metadata"], "t.Annotated[int, 'metadata']", int, ()),
    (t.Annotated[str, "doc", "more"], "t.Annotated[str, 'doc', 'more']", str, ()),
    (
        t.Annotated[list[int], "list doc"],
        "t.Annotated[list[int], 'list doc']",
        list,
        (int,),
    ),
    (
        t.Annotated[t.Optional[str], "nullable"],
        "t.Annotated[t.Optional[str], 'nullable']",
        t.Optional,
        (str,),
    ),
    (te.Literal["one", "two"], "te.Literal['one', 'two']", t.Literal, ()),
    (t.Literal["one", "two"], "t.Literal['one', 'two']", t.Literal, ()),
    # Annotated should be unwrapped to get to the juicy center
    (
        t.Annotated[t.Literal["a", "b"], "status"],
        "t.Annotated[t.Literal['a', 'b'], 'status']",
        t.Literal,
        (),
    ),
    (
        t.Annotated[te.Literal["x", "y"], "code"],
        "t.Annotated[te.Literal['x', 'y'], 'code']",
        t.Literal,
        (),
    ),
    # Nested Annotated
    (
        t.Annotated[t.Annotated[int, "inner"], "outer"],
        "t.Annotated[t.Annotated[int, 'inner'], 'outer']",
        int,
        (),
    ),
    (
        t.Annotated[t.Annotated[t.Annotated[str, "a"], "b"], "c"],
        "t.Annotated[t.Annotated[t.Annotated[str, 'a'], 'b'], 'c']",
        str,
        (),
    ),
    (
        t.Annotated[list[t.Annotated[int, "inner"]], "outer"],
        "t.Annotated[list[t.Annotated[int, 'inner']], 'outer']",
        list,
        (int,),
    ),
)

UNPARSED_INVALID_TYPE_HINTS = (
    None,
    type(None),
    t.Optional,
    list,
    set,
    dict,
    dict[int],  # type: ignore  (intentional error for testing)
    t.Union,
    t.Union[int, str],
)


@pytest.mark.parametrize(
    "raw_type_hint, _, expected_origin, expected_args",
    UNPARSED_VALID_TYPE_HINTS,
)
def test_instantiate_parsed_type_hint(
    raw_type_hint: t.Type,
    _: str,
    expected_origin: t.Type,
    expected_args: tuple[t.Type, ...],
) -> None:
    """
    Instantiates a `type_hint.TypeHint` object and checks the origin and args.
    """
    # Construct the `type_hint.TypeHint` object
    type_hint_object = type_hint.TypeHint(raw_type_hint)

    # Check the origin
    assert type_hint_object.origin is expected_origin

    # Check the args
    assert len(type_hint_object.args) == len(expected_args)

    for arg_should, arg_is in zip(expected_args, type_hint_object.args):
        assert arg_should is arg_is.origin


@pytest.mark.parametrize(
    "_, raw_type_hint, expected_origin, expected_args",
    UNPARSED_VALID_TYPE_HINTS,
)
def test_instantiate_string_type_hint(
    _: t.Type,
    raw_type_hint: str,
    expected_origin: t.Type,
    expected_args: tuple[t.Type, ...],
) -> None:
    """
    Instantiates a `type_hint.TypeHint` object from a string and checks the origin and
    args.
    """
    # Construct the `type_hint.TypeHint` object. Note that the hint is converted to a
    # string first.
    type_hint_object = type_hint.TypeHint(
        raw_type_hint,
        scope=globals(),
    )

    # Check the origin
    assert type_hint_object.origin is expected_origin

    # Check the args
    assert len(type_hint_object.args) == len(expected_args)

    for arg_should, arg_is in zip(expected_args, type_hint_object.args):
        assert arg_should is arg_is.origin


@pytest.mark.parametrize(
    "raw_type_hint",
    UNPARSED_INVALID_TYPE_HINTS,
)
def test_instantiate_invalid_type_hint(
    raw_type_hint: t.Type,
) -> None:
    """
    Instantiates a `type_hint.TypeHint` object from an invalid type hint and checks that
    a `TypeError` is raised.
    """
    with pytest.raises(TypeError):
        type_hint.TypeHint(raw_type_hint)
