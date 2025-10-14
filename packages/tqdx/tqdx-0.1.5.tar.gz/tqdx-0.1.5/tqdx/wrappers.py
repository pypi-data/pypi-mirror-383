from functools import wraps
from typing import Callable, TypeVar

import jax
import jax.core as core

from tqdx.callbacks import close_pbar, init_pbar, update_pbar

Carry = TypeVar("Carry")
X = TypeVar("X")
Y = TypeVar("Y")


@wraps(jax.lax.scan)
def scan(
    f: Callable[[Carry, X], tuple[Carry, Y]],
    init: Carry,
    xs: X | None = None,
    length: int | None = None,
    reverse: bool = False,
    unroll: int | bool = 1,
    _split_transpose: bool = False,
    **kwargs,
) -> tuple[Carry, Y]:
    """A wrapper around jax.lax.scan that adds a progress bar."""

    total = 0
    if xs is not None:
        xs_flat = jax.tree_util.tree_leaves(xs)
        try:
            total = int(xs_flat[0].shape[0])
        except AttributeError as err:
            msg = "scan got value with no leading axis to scan over: {}."
            raise ValueError(
                msg.format(
                    ", ".join(str(x) for x in xs_flat if not hasattr(x, "shape"))
                )
            ) from err
    if length:
        try:
            total = int(length)
        except core.ConcretizationTypeError as err:
            msg = (
                "The `length` argument to `scan` expects a concrete `int` value."
                " For scan-like iteration with a dynamic length, use `while_loop`"
                " or `fori_loop`."
            )

    if total == 0:
        msg = "Either `xs` or `length` has to be provided when calling `scan`"
        raise ValueError(msg)

    id = init_pbar(total=total, **kwargs)

    def wrapped_f(carry_id, x):
        carry, id = carry_id
        carry, y = f(carry, x)
        id = update_pbar(id)
        return (carry, id), y

    (carry, id), ys = jax.lax.scan(
        wrapped_f,
        (init, id),
        xs,
        length=length,
        reverse=reverse,
        unroll=unroll,
        _split_transpose=_split_transpose,
    )
    id = close_pbar(id)
    return carry, ys


@wraps(jax.lax.fori_loop)
def fori_loop(
    lower, upper, body_fun, init_val, *, unroll: int | bool | None = None, **kwargs
):
    """A wrapper around jax.lax.fori_loop that adds a progress bar."""
    total = upper - lower
    id = init_pbar(total=total, **kwargs)

    def wrapped_body_fun(i, val_id):
        val, id = val_id
        out = body_fun(i, val)
        update_pbar(id)
        return (out, id)

    out, id = jax.lax.fori_loop(lower, upper, wrapped_body_fun, (init_val, id), unroll=unroll)
    close_pbar(id)
    return out


def tqdx(f: Callable):
    """A decorator that adds a progress to `jax.lax.scan` or `jax.lax.fori_loop`."""
    if f is jax.lax.scan:
        return scan
    elif f is jax.lax.fori_loop:
        return fori_loop
    else:
        raise ValueError("Function must be jax.lax.scan or jax.lax.fori_loop")
