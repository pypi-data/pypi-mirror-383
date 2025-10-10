from collections.abc import Callable
from functools import wraps
from typing import TypeVar, cast

# from .functional import identity


T = TypeVar("T")
In = TypeVar("In")
Out = TypeVar("Out")


def trivial_decorator[In, Out](func: Callable[[In], Out]) -> Callable[[In], Out]:
    return func


def impure[In, Out](
    callable_or_none: Callable[[In], Out] | None = None,
    message: str = "",
) -> Callable[[In], Out] | Callable[[Callable[[In], Out]], Callable[[In], Out]]:
    if callable_or_none is None:
        return trivial_decorator
    else:
        return callable_or_none


def pure[In, Out](
    callable_or_none: Callable[[In], Out] | None = None,
    message: str = "",
) -> Callable[[In], Out] | Callable[[Callable[[In], Out]], Callable[[In], Out]]:
    if callable_or_none is None:
        return trivial_decorator
    else:
        return callable_or_none


def endo(
    callable_or_none: Callable[[T], T] | None = None,
    message: str = "",
) -> Callable[[T], T] | Callable[[Callable[[In], Out]], Callable[[In], Out]]:
    if callable_or_none is None:
        return trivial_decorator
    else:
        return callable_or_none


def decorate_with_message[In, Out](func: Callable[[In], Out], message: str) -> Callable[[In], Out]:
    @wraps(func)
    def wrapper(*fargs, **fkwargs) -> Out:  # type: ignore
        print(message)

        return func(*fargs, **fkwargs)  # type: ignore

    return cast(Callable[[In], Out], wrapper)


def mutates_instance[In, Out](func: Callable[[In], Out], *mutated: str) -> Callable[[In], Out]:
    message = (
        f"\u001b[31mMutating in place\u001b[0m:         "
        f" via \u001b[33m{func.__name__:<25}\u001b[0m"
        f" in \u001b[34m{func.__module__}\u001b[0m"
    )

    return decorate_with_message(func, message)


def mutates_and_returns_instance[In, Out](
    func: Callable[[In], Out],
    *mutated: str,
) -> Callable[[In], Out]:
    message = (
        f"\u001b[31mMutating\u001b[0m"
        f"{(' ' * bool(mutated)) + ', '.join(mutated)}"
        f" \u001b[31mand returning instance of\u001b[0m: {func.__class__.__name__}"
        f" via \u001b[33m{func.__name__:<25}\u001b[0m"
        f" in \u001b[34m{func.__module__}\u001b[0m"
    )

    return decorate_with_message(func, message)


def mutates[In, Out](func: Callable[[In], Out], *mutated: str) -> Callable[[In], Out]:
    message = (
        f"Mutating \u001b[36m{', '.join(mutated):<50}\u001b[0m"
        f" via \u001b[33m{func.__name__:<25}\u001b[0m"
        f" in \u001b[34m{func.__module__:<40}\u001b[0m"
    )

    return decorate_with_message(func, message)


def refactor[In, Out](func: Callable[[In], Out], message: str = "") -> Callable[[In], Out]:
    message = (
        f"\u001b[36mREFACTOR\u001b[0m"
        f" \u001b[33m{func.__name__}\u001b[0m"
        f" in \u001b[34m{func.__module__.replace('consilium.', '.')}\u001b[0m."
        f"\n    {message}"
    )

    return decorate_with_message(func, message)
