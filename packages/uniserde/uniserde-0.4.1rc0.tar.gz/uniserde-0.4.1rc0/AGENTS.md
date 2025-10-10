# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`uniserde` is a Python library for convention-based serialization and deserialization of Python objects to/from JSON and BSON. It uses type annotations to automatically handle conversion without requiring manual serialization code.

Key features:
- Automatic ser/des for dataclasses and regular classes using type hints
- Support for JSON and BSON formats
- MongoDB schema generation from Python types
- Lazy deserialization for performance optimization
- Custom handlers for specialized types
- Name mapping conventions (e.g., Python snake_case to JSON camelCase)

## Development Commands

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_json.py

# Run specific test
uv run pytest tests/test_json.py::test_name -k "pattern"

# Run tests with verbose output
uv run pytest -v
```

### Linting
```bash
# Run ruff linter
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .
```

### Building
```bash
# Build the package
uv build
```

## Architecture

### Core Design: Dynamic Code Generation

The library's performance comes from **dynamically generating specialized serialization/deserialization functions** for each type at runtime. This is a critical architectural detail:

1. **TypeHint** (`type_hint.py`): Normalizes Python type hints into a comparable, hashable representation. Handles generics, Optional, Union, Literal, Annotated, etc.

2. **SerdeCache** (`serde_cache.py`): Abstract base for caching handlers. When a new type is encountered:
   - Generates Python code (via `Codegen`) to handle that specific type
   - Compiles the code using `exec()`
   - Caches the resulting function for reuse
   - This means the first encounter is slow (code generation) but subsequent uses are fast

3. **Codegen** (`codegen.py`): Builds Python code as strings. Tracks:
   - Variable names (auto-generated unique IDs)
   - External processors (handlers for nested types)
   - Exposed values (runtime dependencies needed by generated code)

4. **Handler Builders vs Handlers**:
   - `HandlerBuilder`: Function that **generates code** (string) for processing a type
   - `InternalHandler`: Actual runtime function that **processes values**
   - The cache converts builders → code → compiled handlers

### Serialization/Deserialization Flow

**JsonSerde** and **BsonSerde** (`json_serde.py`, `bson_serde.py`) are the public APIs. Each maintains three caches:
- Serialization cache (type → JSON/BSON)
- Deserialization cache (JSON/BSON → type)
- Schema cache (type → MongoDB schema, BSON only)

Format-specific logic lives in:
- `json_serialize.py` / `json_deserialize.py`
- `bson_serialize.py` / `bson_deserialize.py`
- `schema_mongodb.py` (MongoDB schema generation)

Each implements handlers for built-in types (int, str, list, dict, etc.) and class-based types.

### Lazy Deserialization

**lazy_wrapper.py** implements deferred field deserialization:
- Creates instances using `object.__new__()` (skips `__init__`)
- Injects a custom `__getattr__` that deserializes fields on first access
- Stores raw field values in `_uniserde_remaining_fields_`
- Caches deserialized values in instance `__dict__`

**Important**: Lazy mode skips validation for unaccessed fields. Only use with trusted data.

### Name Mapping

**case_convert.py** provides functions to map Python naming conventions to document conventions:
- Attributes: `snake_case` → `camelCase` (or identity)
- Classes: `UpperCamelCase` → `camelCase` (or identity)
- Enums: `ALL_CAPS` → `camelCase` (or identity)

Default (v0.4+) preserves Python names. Use `JsonSerde.new_camel_case()` or `BsonSerde.new_camel_case()` for camelCase conventions.

### Custom Handlers

Three extension points:
1. **Custom handlers**: Pass `custom_serializers`/`custom_deserializers` dicts to Serde constructors
2. **Class methods**: Define `_uniserde_as_json_`, `_uniserde_from_json_`, etc. on classes
3. **@as_child decorator** (`utils.py`): Marks polymorphic base classes. Adds `type` field to serialized form for correct deserialization

### Special Types

- **ObjectId** (`objectid_proxy.py`): Proxy for `bson.ObjectId` to avoid hard dependency
- **Error handling** (`errors.py`): Single `SerdeError` exception type
- **Type definitions** (`typedefs.py`): Type aliases like `Jsonable`, `JsonDoc`, `Bsonable`, `BsonDoc`

## Important Conventions

### Version Compatibility
- v0.4+ changed default naming from camelCase to identity (preserves Python names)
- Set `UNISERDE_BACKWARDS_COMPATIBILITY` env var to enable legacy imports (see `compat.py`)

### Performance Best Practices
- **Reuse Serde instances**: Handler cache is per-instance. Create few instances and reuse them
- The first serialization/deserialization of a type is slower (code generation overhead)
- Subsequent operations on the same type are fast (cached compiled handlers)

### Type Annotations Are Required
- All class attributes must have type hints
- Uses `utils.get_class_attributes_recursive()` to collect annotations from entire MRO
- Generic types (list, dict) must have explicit type parameters when serializing

## Coding Style

### Imports

**Core Principle**: Import modules, not values. Then refer to values by their fully qualified name (FQN).

```python
# Preferred
import mypackage.repository
repo = mypackage.repository.Repository()

# Avoid
from mypackage.repository import Repository
repo = Repository()  # Where does this come from?
```

**Exceptions**:

1. **Public API values**: Values that are part of a package's public API should be easily accessible from the package root.

   ```python
   import mypackage as mp
   repo = mp.Repository()  # ✅ Clean, clear it's from mypackage
   query = mp.Query()      # ✅ Part of public API
   ```

   This requires re-exporting at the package level (`mypackage/__init__.py`), using the `import Foo as Foo` pattern to make the re-export explicit.

2. **Ubiquitous values**: Very common types/modules that everyone knows can be imported directly.

   ```python
   from datetime import datetime  # ✅ Ubiquitous, everyone knows it
   from pathlib import Path       # ✅ Standard library, well-known
   ```

3. **Common module aliases**: If a module is extremely common, use a well-known short alias.

   ```python
   import typing as t       # ✅ Standard convention
   import numpy as np       # ✅ Standard convention
   import mypackage as mp   # ✅ Project-specific convention
   ```

**Benefits**:
- Clear provenance: You always know where a value comes from
- Avoids namespace pollution: No mystery about what's in scope
- Prevents conflicts: Two modules can have `Repository` without collision
- Better IDE support: Autocomplete and go-to-definition work better
- Easier refactoring: Changing module structure doesn't break imports everywhere

## Test Structure

- `tests/models.py`: Shared test data models
- `tests/test_json.py`: JSON serialization tests
- `tests/test_bson.py`: BSON serialization tests
- `tests/test_mongodb_schema.py`: Schema generation tests
- `tests/test_lazy.py`: Lazy deserialization tests
- `tests/test_type_info.py`: TypeHint class tests

## Development Files (Not for Production)
- `devel.py`, `lazytest.py`, `speedtest.py`: Development/benchmarking scripts
- `wip/`: Work in progress
- `scripts/`: Code generation utilities for other languages


