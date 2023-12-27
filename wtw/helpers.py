import inspect
from typing import Callable


def validate_keys(d: dict, items: list) -> dict:
    """Validate if a dict's keys are in a list."""
    for k, v in d.items():
        if k not in items:
            d.pop(k)
    return d


def validate_kwargs(kwargs: dict, f: Callable) -> dict:
    """
    Validate if kwargs are valid for a function.

    Removes invalid kwargs from kwargs dict.
    """
    argspec = inspect.getfullargspec(f)
    argspec_args = argspec.args
    argspec_args.remove("self")
    kwargs = validate_keys(kwargs, argspec_args)
    return kwargs
