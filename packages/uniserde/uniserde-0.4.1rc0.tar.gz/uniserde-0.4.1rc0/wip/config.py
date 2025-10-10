from __future__ import annotations
import typing_extensions as te
import typing as t

from pathlib import Path
import uniserde

import uniserde.case_convert


class Config:
    """
    Easy way to load and save configuration files in TOML format.

    The configuration file is loaded once, and then cached. Any modified values
    are remembered and written back in one go later on. Writing changes to the
    file is done atomically and preserves comments and formatting in the file.
    """

    # Where to load the config from and save it back to
    uniserde_config_path: Path | None

    # Keeps track of any keys which were changed and need to be written back
    # to the file
    _uniserde_dirty_keys: set[str]

    def __init_subclass__(cls) -> None:
        # This class depends on `tomlkit`. Make sure it's installed
        try:
            import tomlkit  # type: ignore
        except ImportError:
            raise RuntimeError(
                "`uniserde.Config` requires the `tomlkit` package to be installed."
            ) from None

        # Make sure all fields have default values, i.e. the class can be
        # instantiated without any arguments.
        try:
            cls()
        except TypeError:
            raise TypeError(
                f"`{cls.__name__}` must be instantiable without any arguments. Make sure all fields have default values."
            ) from None

    def __init__(self) -> None:
        self.uniserde_config_path = None
        self._uniserde_dirty_keys = set()

    @classmethod
    def uniserde_load(cls, path: Path) -> te.Self:
        """
        Creates a new instance of this class, populating it with the contents of
        the TOML file at the given path.

        Any missing or invalid fields are replaced with the fields' default
        values.
        """
        import tomlkit  # type: ignore

        # Try to load the file from disk
        try:
            with path.open() as f:
                raw_values = tomlkit.load(f).unwrap()

        except Exception:
            raw_values = {}

        # Instantiate the result with default values
        self = cls()

        # Deserialize each field individually, imputing defaults as needed
        for py_field_name, field_type in uniserde.get_global_class_attributes(
            cls
        ).items():
            doc_field_name = uniserde.case_convert.all_lower_to_kebab_case(
                py_field_name
            )

            try:
                raw_field = raw_values[doc_field_name]
                field_value = uniserde.from_json(raw_field, field_type)
            except (KeyError, uniserde.SerdeError):
                pass
            else:
                setattr(self, py_field_name, field_value)

        # Setting all of the fields will make the result think that they are
        # dirty. Clear that flag.
        self._uniserde_dirty_keys.clear()

        # Done!
        return self

    def uniserde_dump(self) -> None:
        """
        Write the cached config values back to the `self.config_path` file.
        """
        assert self.uniserde_config_path is not None
        import tomlkit  # type: ignore
        import tomlkit.exceptions  # type: ignore

        # Make sure the parent directory exists
        self.uniserde_config_path.parent.mkdir(parents=True, exist_ok=True)

        # Fetch an up-to-date copy of the file contents, with all formatting
        # intact
        full_dump = uniserde.as_json(self)

        try:
            with self.uniserde_config_path.open() as f:
                new_toml_dict = tomlkit.load(f)

        # If it can't be read, preserve all known values
        except (OSError, tomlkit.exceptions.TOMLKitError):
            new_toml_dict = tomlkit.TOMLDocument()

            for doc_field_name, value in full_dump.items():
                new_toml_dict[doc_field_name] = value

        # Otherwise add just the dirty keys
        else:
            for py_field_name in self._uniserde_dirty_keys:
                doc_field_name = uniserde.case_convert.all_lower_to_kebab_case(
                    py_field_name
                )
                new_toml_dict[doc_field_name] = full_dump[doc_field_name]

        # Dump the new TOML
        with self.uniserde_config_path.open("w") as f:
            tomlkit.dump(new_toml_dict, f)

        # All values have been saved and are now clean
        self._uniserde_dirty_keys.clear()

    def __setattr__(self, name: str, value: t.Any) -> None:
        # Store the new value
        self.__dict__[name] = value

        # Remember that this key was changed
        self._uniserde_dirty_keys.add(name)

    def __enter__(self) -> "Config":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        # Make sure to write any changes back to the toml file
        self.uniserde_dump()
