from __future__ import annotations

import threading
from functools import partial, wraps
from typing import Any, Callable

import equinox as eqx
import jax
import numpy as np
from jax import lax
from jax import numpy as jnp


# TODO: Consider moving this to a standalone Equinox utilities library
def clone_state(state: eqx.nn.State) -> eqx.nn.State:
    """
    Clone an Equinox state.

    Equinox does not allow reuse of states. Cloning in this way bypasses this restriction.
    """
    leaves, treedef = jax.tree.flatten(state)
    state_clone = jax.tree.unflatten(treedef, leaves)
    return state_clone


# TODO: Consider moving this to a standalone Equinox utilities library
class _FilterScan(eqx.Module):

    @property
    def __wrapped__(self):
        return lax.scan

    def __call__(
        self,
        f,
        init,
        xs=None,
        length=None,
        reverse: bool = False,
        unroll: int | bool = 1,
        _split_transpose: bool = False,
    ):
        init_arr, static = eqx.partition(init, eqx.is_array)

        def _f(carry_arr, x):
            carry = eqx.combine(carry_arr, static)
            carry, y = f(carry, x)
            new_carry_arr, new_static = eqx.partition(carry, eqx.is_array)
            assert eqx.tree_equal(
                static, new_static
            ), "Non-array carry of filter_scan must not change."
            return new_carry_arr, y

        carry_arr, ys = lax.scan(
            f=_f,
            init=init_arr,
            xs=xs,
            length=length,
            reverse=reverse,
            unroll=unroll,
            _split_transpose=_split_transpose,
        )
        return eqx.combine(carry_arr, static), ys


filter_scan = eqx.module_update_wrapper(_FilterScan())


def debug_wrapper[**InType](
    func: Callable[InType, Any], ordered: bool = False, thread: bool | None = None
) -> Callable[InType, None]:
    """
    Return a JIT‑safe version of *func*.

    :param func: The function to wrap.
    :param ordered: If True, the callback will be executed in the order of the arguments
    :param thread: If True, the callback will be executed in a separate thread.
    """
    if thread is None:
        thread = not ordered

    if ordered and thread:
        # TODO: Add a warning or error here
        pass

    def _callback(*args: InType.args, **kwargs: InType.kwargs) -> None:
        if thread:
            threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True).start()
        else:
            func(*args, **kwargs)

    @wraps(func)
    def wrapped(*args: InType.args, **kwargs: InType.kwargs) -> None:
        jax.debug.callback(_callback, *args, **kwargs, ordered=ordered)

    return wrapped


def debug_with_numpy_wrapper(
    func: Callable[..., Any], ordered: bool = False, thread: bool | None = None
) -> Callable[..., None]:
    """
    Like `debug_wrapper` but converts every jax.Array/`jnp.ndarray` argument
    to a plain `numpy.ndarray` before calling *func*.

    It is impossible with Python's current type system to express the transformation so
    parameter information is lost.
    """

    @partial(debug_wrapper, ordered=ordered, thread=thread)
    @wraps(func)
    def wrapped(*args, **kwargs) -> None:
        args, kwargs = jax.tree.map(
            lambda x: np.asarray(x) if isinstance(x, jnp.ndarray) else x, (args, kwargs)
        )
        func(*args, **kwargs)

    return wrapped


def debug_with_list_wrapper(
    func: Callable[..., Any], ordered: bool = False, thread: bool | None = None
) -> Callable[..., None]:
    """
    Like `debug_wrapper` but converts every jax.Array/`jnp.ndarray` argument
    to a plain list before calling *func*.

    It is impossible with Python's current type system to express the transformation so
    parameter information is lost.
    """

    @partial(debug_wrapper, ordered=ordered, thread=thread)
    @wraps(func)
    def wrapped(*args, **kwargs) -> None:
        args, kwargs = jax.tree.map(
            lambda x: (
                np.asarray(x).tolist()
                if isinstance(x, (jnp.ndarray, np.ndarray))
                else x
            ),
            (args, kwargs),
        )
        func(*args, **kwargs)

    return wrapped
