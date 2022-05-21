"""A custom, minimal, incomplete implementation of Python's dataclasses. The current features:

 - Instance attributes can be specified using class attribute syntax.
 - Custom `__init__` and `__str__` methods are auto-generated to handle initialization,
     and the custom `__init__` allows for a `__post_init__` method to be defined to customize initialization.
"""

from itertools import zip_longest
from typing import Any, Mapping, Callable

# TODO: There's actually more we may need to be cautious of.
_SPECIAL_ATTRS = {"__module__", "__qualname__", "__annotations__"}

# So the user can use whatever default value they want without us needing to worry about clashing.
# Will always compare as different when compared using "is".
_SENTINEL = object()


class _Field:
    def __init__(self, name: str, annotation: type, default=_SENTINEL):
        self.name = name
        self.annotation = annotation
        self.default = default

    def has_default(self) -> bool:
        return self.default is not _SENTINEL


def _collect_fields(namespace: Mapping[str, Any]) -> dict[str, _Field]:
    """Returns a mapping of field names to field objects.
    """
    annot = namespace.get("__annotations__", {})

    fields = {}
    for name, annotation in annot.items():
        if name not in _SPECIAL_ATTRS:
            fields[name] = _Field(name, annotation, namespace.get(name, _SENTINEL))
    return fields


# TODO: I feel like there's a cleaner way of doing this
def _assert_defaults_are_last(fields: Mapping[str, _Field]):
    it = iter(fields.values())
    for field in it:
        if field.has_default():
            break
    for field in it:
        if not field.has_default():
            raise TypeError(f"non-default argument '{field.name}' follows default argument")


def _remove_class_attributes(namespace: Mapping[str, Any], fields: Mapping[str, _Field]) -> dict[str, Any]:
    return {k:v for k, v in namespace.items() if k not in fields}


def _new_init(fields: dict[str, _Field]) -> Callable:
    """The custom __init__ method to be given to the new class."""
    def init(future_self, *args, **kwargs):
        n_args_passed = len(args) + len(kwargs)
        if n_args_passed > len(fields):
            raise TypeError(f"{type(future_self).__name__}.__init__() takes at most {len(fields)}"
                            f" arguments, but {n_args_passed} were given.")

        fields_with_passed = zip_longest(fields.items(), args, fillvalue=_SENTINEL)

        missing_values = []
        for (name, field), maybe_positional in fields_with_passed:
            # If it's not a kwarg, it must either be a positional or missing.
            passed_value = kwargs.get(name, maybe_positional)

            # TODO: Eww
            if not field.has_default() and passed_value is _SENTINEL:
                missing_values.append(name)
            else:
                value = field.default if passed_value is _SENTINEL else passed_value
                setattr(future_self, name, value)

        if missing_values:
            raise TypeError(f"{type(future_self).__name__}.__init__()"
                            f" missing {len(missing_values)} required positional arguments:"
                            f" {', '.join(missing_values)}")

        if hasattr(future_self, "__post_init__"):
            future_self.__post_init__()

    return init


def _new_str(fields: dict[str, _Field]) -> Callable:
    """The custom __str__ method to be given to the new class."""
    def _str(future_self):
        pairs = [f"{name}={getattr(future_self, name)}" for name in fields]
        return f"{type(future_self).__name__}({', '.join(pairs)})"
    return _str


class MyDataclassMetaclass(type):
    def __new__(mcs, name, bases, namespace, **kwargs):
        name_to_field = _collect_fields(namespace)
        _assert_defaults_are_last(name_to_field)
        namespace = _remove_class_attributes(namespace, name_to_field)
        namespace["__init__"] = _new_init(name_to_field)
        namespace["__str__"] = _new_str(name_to_field)
        namespace["__slots__"] = tuple(name_to_field.keys())

        new_class = super().__new__(mcs, name, bases, namespace, **kwargs)
        return new_class


class MyDataclass(metaclass=MyDataclassMetaclass):
    """To be inherited from to make a class a dataclass."""
    pass


