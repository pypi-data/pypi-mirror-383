# Convention Based, Effortless Serialization & Deserialization

`uniserde` can convert Python classes to/from JSON and BSON without effort from
your side. Simply define the classes, and the library does the rest.

Define your types as classes with type annotations, and use one of `uniserde`'s
serializers / deserializers:

```py
import uniserde
from datetime import datetime, timezone
from dataclasses import dataclass
from bson import ObjectId


@dataclass
class Person:
    id: ObjectId
    name: str
    birth_date: datetime


betty = Person(
    id=ObjectId(),
    name="Betty",
    birth_date=datetime(year=1988, month=12, day=1, tzinfo=timezone.utc),
)

serde = uniserde.JsonSerde()
print(serde.as_json(betty))
```

This will print a dictionary similar to this one

```py
{
    'id': '62bc6c77792fc617c52499d0',
    'name': 'Betty',
    'birth_date': '1988-12-01T00:00:00+00:00'
}
```

You can easily convert this to a string using Python's built-in `json` module if
that's what you're after.

## API

The API is extremely simple. Functions/Classes you might be interested in are:

- `JsonSerde` is used to serialize/deserialize Python values to/from JSON. It
  takes some configuration options like custom handlers for specific types.

  Use `JsonSerde.as_json` to serialize a Python object to JSON, and
  `JsonSerde.from_json` to deserialize a JSON object to a Python object.

- `BsonSerde` is like `JsonSerde`, but for BSON. In addition to serialization &
  deserialization, it also supports MongoDB schema generation.

  Use `BsonSerde.as_bson` to serialize a Python object to BSON,
  `BsonSerde.from_bson` to deserialize a BSON object to a Python object, and
  `BsonSerde.as_mongodb_schema` to generate a MongoDB schema from a Python
  class.

- `SerdeErrro`: The error raised when something goes wrong during serialization
  or deserialization, e.g. when a required field is missing.

- Sometimes a class simply acts as a type-safe base, but you really just want to
  serialize the children of that class. In that case you can decorate the class
  with `@as_child`. This will store an additional `type` field in the result, so
  the correct child class can be instantiated when deserializing.

- Custom serialization / deserialization can be achieved by giving custom
  handlers to the Serde instances or by defining the appropriate methods on your
  classes:

  - `_uniserde_as_json_`
  - `_uniserde_as_bson_`
  - `_uniserde_from_json_`
  - `_uniserde_from_bson_`
  - `_uniserde_as_mongodb_schema_`

  When called, these are passed the same parameters:

  - The `JsonSerde` / `BsonSerde` instance doing the
    serialization/deserialization
  - The value to be serialized/deserialized
  - As which type to serialize/deserialize the value (This is needed e.g. for
    generics, that may not know the type of all of their child attributes).

  (`_uniserde_as_monogodb_schema_` only receives the Serde instance and the
  type, since there is no value to process.)

- The library also exposes a couple handy type definitions:
  - `Jsonable`, `Bsonable` -- Any type which can occur in a JSON / BSON file
    respectively, i.e. (bool, int, float, ...)
  - `JsonDoc`, `BsonDoc` -- A dictionary mapping strings to `Jsonable`s /
    `Bsonable`

### JSON Conventions

| Python               | JSON              | Notes                                                                                                                 |
| -------------------- | ----------------- | --------------------------------------------------------------------------------------------------------------------- |
| `bool`               | `bool`            |                                                                                                                       |
| `int`                | `float`           |                                                                                                                       |
| `float`              | `float`           |                                                                                                                       |
| `str`                | `str`             |                                                                                                                       |
| `tuple`              | `list`            |                                                                                                                       |
| `list`               | `list`            |                                                                                                                       |
| `set`                | `list`            |                                                                                                                       |
| `Optional`           | value or `None`   |                                                                                                                       |
| `Any`                | as-is             | The value is kept unchanged, without any checks.                                                                      |
| `Literal[str]`       | `str`             |                                                                                                                       |
| `enum.Enum`          | `str`             | Enum values are mapped to their _name_ (**NOT value!**)                                                               |
| `enum.Flag`          | `list[str]`       | Each flag is encoded the same way a regular `enum.Enum` value would.                                                  |
| custom class         | `dict`            | Each attribute is stored as key, in _lowerCamelCase_. If marked with `as_child`, an additional `type` field is added. |
| `bytes`              | `str`             | base64 encoded                                                                                                        |
| `datetime.datetime`  | `str`             | as ISO 8601 - with timezone. Naïve datetimes are intentionally not supported. Do yourself a favor and don't use them. |
| `datetime.timedelta` | `float`           | duration, in seconds                                                                                                  |
| `dict[K, V]`         | `dict[str, ...]`  | Dictionary keys can be `str` or `int`                                                                                 |
| `bson.ObjectId`      | `str`             |                                                                                                                       |
| `pathlib.Path`       | `str`             | Paths are made absolute before serialization.                                                                         |
| `uuid.UUID`          | `str`             |                                                                                                                       |

### BSON Conventions

BSON mostly uses the same conventions as JSON, with just a few changes:

| Python              | BSON                | Notes                                                                                    |
| ------------------- | ------------------- | ---------------------------------------------------------------------------------------- |
| `bytes`             | `bytes`             |                                                                                          |
| `datetime.datetime` | `datetime.datetime` | Serialization requires a timezone be set. Deserialization imputes UTC, to match MongoDB. |
| `bson.ObjectId`     | `bson.ObjectId`     |                                                                                          |
| `uuid.UUID`         | `uuid.UUID`         |                                                                                          |

## MongoDB Schema Generation

If you are working with MongoDB you will come to appreciate the automatic schema
generation. Calling `uniserde.as_mongodb_schema` on any supported class will
return a MongoDB compatible JSON schema without hassle.

For example, here's the result of `uniserde.as_mongodb_schema(Person)` with the
`Person` class above:

```py
{
    'type': 'object',
    'properties': {
        'id': {
            'bsonType': 'objectId'
        },
        'name': {
            'type': 'string'
        },
        'birth_date': {
            'bsonType': 'date'
        }
    },
    'additionalProperties': False,
    'required': [
        'id',
        'name',
        'birth_date'
    ]
}
```

## Lazy Deserialization

Normally, serialization happens all at once: You tell `uniserde` to create a
class instance from a JSON, `uniserde` processes all of the fields and returns
the finished class.

This works great, but can be wasteful if you are working with large documents
and only need to access few fields. To help with this, you can pass `lazy=True`
when deserializing any object. `uniserde` will then hold off deserializing
fields until they are accessed for the first time, saving precious processing
time.

**A word of caution:** Data is validated as it is deserialized. Since lazy
deserialization defers work until the data is accessed, this means any data you
don't access also won't be validated. Thus, lazy serialization can be a very
powerful tool for speeding up interactions with large objects, but you should
only use when you are absolutely certain the data is correct. (For example
because you have just fetched the object from your own, trusted, database.)

## Maximizing performance

Whenever `uniserde` needs to serialize a type, it builds a handler specifically
for that type. That handler is then cached in the active Serde instance, so that
any future serialization / deserialization of that type is much faster. Thus, to
get maximum performance, you can create one global Serde instance configure it
to your liking then reuse it every time you need one.

## Limitations

- Recursive types are not supported - Types that reference themselves (directly
  or indirectly) will result in a `SerdeError`.
- Support for `Union` is currently very limited. Really only `Optional` is
  supported (which Python internally maps to `Union`)
- `Literal` currently only supports strings
- Examples for custom serialization / deserialization
- Extend `as_child`, to allow marking some classes as abstract. i.e. their
  parents/children can be serialized, but not those classes themselves
- Being able to specify additional limitations to fields would be nice:
  - must match regex
  - minimum / maximum
  - custom validation functions
- more Unit tests (custom de-serializers!?)
- Add more examples to the README
  - show custom serializers/deserializers
  - recommended usage
- calling `uniserde.serialize` on non-classes causes problems, because the
  serialization `as_type` is guessed incorrectly. e.g. `[1, 2, 3]` will be
  incorrectly serialized as `list` rather than `list[int]`.
