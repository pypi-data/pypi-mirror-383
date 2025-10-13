from __future__ import annotations

from typing import Callable

import diffrax
import equinox as eqx
from jax import lax
from jax import nn as jnn
from jax import numpy as jnp
from jax import random as jr
from jaxtyping import Array, Float, Int, Key, PyTree, Shaped

from ..base_model import AbstractStatefulModel
from .term import AbstractNCDETerm, MLPNCDETerm

type Coeffs = tuple[
    PyTree[Shaped[Array, "times-1 ?*shape"]],
    PyTree[Shaped[Array, "times-1 ?*shape"]],
    PyTree[Shaped[Array, "times-1 ?*shape"]],
    PyTree[Shaped[Array, "times-1 ?*shape"]],
]

type CDEState = tuple[
    Float[Array, " n"],  # Time
    Float[Array, " n input_size"],  # Inputs
    Float[Array, " n latent_size"],  # States
]


class AbstractNeuralCDE[
    LatentType: Callable[[Array], Float[Array, " latent_size"]],
    OutputType: Callable[[Array], Float[Array, " latent_size"]],
](
    AbstractStatefulModel[
        [Float[Array, ""], Float[Array, " in_size"]], Float[Array, " out_size"]
    ],
):
    """
    Abstract base class for Neural Controlled Differential Equations (NCDEs).

    x is used to denote the input, t is the time, z is the latent state, and y is the
    output. _s is used to denote all states of a variable (e.g. zs is the latent states
    at all times) and _1 is used to denote the last state of a variable (e.g. z1 is the
    latent state at the last time).

    The state_size defines the maximum number of inputs and corresponding states that
    are tracked. In theory the latest latent vector should contain all the important
    information about the history of inputs and states, but the longer the history
    allows more accurate gradients to be computed for back propagation through time.
    Inference mode can be used to disable the history and only use the latest state for
    faster computation without back propagation through time.
    """

    term: eqx.AbstractVar[AbstractNCDETerm]
    solver: eqx.AbstractVar[type[diffrax.AbstractSolver]]

    in_size: eqx.AbstractVar[int]
    latent_size: eqx.AbstractVar[int]
    out_size: eqx.AbstractVar[int]

    initial: eqx.AbstractVar[LatentType]
    output: eqx.AbstractVar[OutputType]
    time_in_input: eqx.AbstractVar[bool]

    state_size: eqx.AbstractVar[int]
    state_index: eqx.AbstractVar[eqx.nn.StateIndex[CDEState]]

    inference: eqx.AbstractVar[bool]

    def empty_state(self) -> CDEState:
        times = jnp.full((self.state_size,), jnp.nan)
        inputs = jnp.full((self.state_size, self.in_size), jnp.nan)
        states = jnp.full((self.state_size, self.latent_size), jnp.nan)
        return times, inputs, states

    def coeffs(self, ts: Float[Array, " n"], xs: Float[Array, " n in_size"]) -> Coeffs:
        if self.time_in_input:
            xs = jnp.concatenate([ts[:, None], xs], axis=1)

        coeffs = diffrax.backward_hermite_coefficients(ts, xs)

        return coeffs

    def solve(
        self,
        ts: Float[Array, " n"],
        z0: Float[Array, " latent_size"],
        coeffs: Coeffs,
    ) -> Float[Array, " n latent_size"]:
        solver = self.solver()
        if isinstance(solver, diffrax.AbstractAdaptiveSolver):
            stepsize_controller = diffrax.PIDController(rtol=1e-3, atol=1e-6)
            dt0 = None
        else:
            stepsize_controller = diffrax.ConstantStepSize()
            dt0 = jnp.nanmean(jnp.diff(ts))

        control = diffrax.CubicInterpolation(ts, coeffs)
        term = diffrax.ControlTerm(self.term, control).to_ode()
        saveat = diffrax.SaveAt(ts=ts)

        solution = diffrax.diffeqsolve(
            term,
            solver,
            t0=jnp.nanmin(ts),
            t1=jnp.nanmax(ts),
            dt0=dt0,
            y0=z0,
            stepsize_controller=stepsize_controller,
            saveat=saveat,
        )

        assert solution.ys is not None
        zs = solution.ys

        zs = jnp.asarray(jnp.where(jnp.isnan(ts[:, None]), jnp.nan, zs))

        return zs

    def z0(
        self, t0: Float[Array, ""], x0: Float[Array, " in_size"]
    ) -> Float[Array, " latent_size"]:
        if self.time_in_input:
            return self.initial(
                jnp.concatenate([x0, jnp.expand_dims(t0, axis=-1)], axis=-1)
            )
        else:
            return self.initial(x0)

    @staticmethod
    def latest_index(ts: Float[Array, " num_steps"]) -> Int[Array, ""]:
        return jnp.nanargmax(ts)

    def next_state(
        self,
        state: eqx.nn.State,
        t1: Float[Array, ""],
        x1: Float[Array, " in_size"],
    ) -> tuple[
        Float[Array, " num_steps"],
        Float[Array, " num_steps input_size"],
        Float[Array, " num_steps latent_size"],
    ]:
        """Add new time and input pair to the state."""
        ts, xs, zs = state.get(self.state_index)
        latest_index = self.latest_index(ts)
        ts = eqx.error_if(
            ts,
            t1 <= ts[latest_index],
            "new input and time must be later than all previous",
        )

        def shift() -> tuple[
            Float[Array, " num_steps"],
            Float[Array, " num_steps input_size"],
            Float[Array, " num_steps latent_size"],
        ]:
            """Shift the saved times and inputs to make room for the new pair."""
            return (
                jnp.roll(ts, -1).at[-1].set(t1),
                jnp.roll(xs, -1, axis=0).at[-1].set(x1),
                jnp.roll(zs, -1, axis=0).at[-1].set(jnp.nan),
            )

        def insert() -> tuple[
            Float[Array, " num_steps"],
            Float[Array, " num_steps input_size"],
            Float[Array, " num_steps latent_size"],
        ]:
            """Insert the new time and input pair at the end of the saved times and inputs."""
            return ts.at[latest_index + 1].set(t1), xs.at[latest_index + 1].set(x1), zs

        ts, xs, zs = lax.cond(
            latest_index == self.state_size - 1,
            shift,
            insert,
        )

        return ts, xs, zs

    def __call__(
        self,
        state: eqx.nn.State,
        t1: Float[Array, ""],
        x1: Float[Array, " in_size"],
        inference: bool | None = None,
    ) -> tuple[eqx.nn.State, Float[Array, " out_size"]]:
        """
        Compute the next state and output given the current state and input.
        """
        ts, xs, zs = self.next_state(state, t1, x1)

        if inference or self.inference:
            z0 = self.z0(ts[0], xs[0])
            z1 = self.solve(ts, z0, self.coeffs(ts, xs))[self.latest_index(ts)]
        else:
            z0 = zs[self.latest_index(ts)]
            slice_index = jnp.min(
                jnp.asarray([self.state_size - 2, self.latest_index(ts)])
            )
            sliced_ts = lax.dynamic_slice(ts, (slice_index,), (2,))
            sliced_xs = lax.dynamic_slice(xs, (slice_index, 0), (2, self.in_size))

            z1 = self.solve(sliced_ts, z0, self.coeffs(sliced_ts, sliced_xs))[1]

        zs = zs.at[self.latest_index(ts)].set(z1)
        state = state.set(self.state_index, (ts, xs, zs))

        return state, self.output(z1)

    def t1(self, state: eqx.nn.State) -> Float[Array, ""]:
        """Get the last time in the state."""
        ts, _, _ = state.get(self.state_index)
        return jnp.nanmax(ts)

    def ts(self, state: eqx.nn.State) -> Float[Array, " n"]:
        """Get all times in the state."""
        ts, _, _ = state.get(self.state_index)
        return ts

    def x1(self, state: eqx.nn.State) -> Float[Array, " in_size"]:
        """Get the last input in the state."""
        ts, xs, _ = state.get(self.state_index)
        return xs[self.latest_index(ts)]

    def xs(self, state: eqx.nn.State) -> Float[Array, " n in_size"]:
        """Get all inputs in the state."""
        _, xs, _ = state.get(self.state_index)
        return xs

    def z1(
        self, state: eqx.nn.State, inference: bool | None = None
    ) -> Float[Array, " latent_size"]:
        """Get the last state in the state."""
        ts, xs, zs = state.get(self.state_index)

        if inference or self.inference:
            z0 = self.z0(ts[0], xs[0])
            z1 = self.solve(ts, z0, self.coeffs(ts, xs))[self.latest_index(ts)]
        else:
            z1 = zs[self.latest_index(ts)]

        return z1

    def zs(
        self, state: eqx.nn.State, inference: bool | None = None
    ) -> Float[Array, " n latent_size"]:
        """Get all states in the state."""

        ts, xs, zs = state.get(self.state_index)

        if inference or self.inference:
            z0 = self.z0(ts[0], xs[0])
            zs = self.solve(ts, z0, self.coeffs(ts, xs))

        return zs

    def reset(self, state: eqx.nn.State) -> eqx.nn.State:
        """Reset the state to an empty state."""
        return state.set(self.state_index, self.empty_state())


class MLPNeuralCDE(AbstractNeuralCDE):

    term: MLPNCDETerm
    solver: type[diffrax.AbstractSolver]

    initial: eqx.nn.MLP
    output: eqx.nn.MLP
    time_in_input: bool

    in_size: int
    latent_size: int
    out_size: int

    state_size: int
    state_index: eqx.nn.StateIndex[CDEState]

    inference: bool

    def __init__(
        self,
        in_size: int,
        out_size: int,
        latent_size: int,
        width_size: int,
        depth: int,
        field_activation: Callable[
            [Float[Array, " width"]], Float[Array, " width"]
        ] = jnn.softplus,
        field_final_activation: Callable[
            [Float[Array, " width"]], Float[Array, " width"]
        ] = jnn.tanh,
        initial_state_activation: Callable[
            [Float[Array, " width"]], Float[Array, " width"]
        ] = jnn.relu,
        initial_state_final_activation: Callable[
            [Float[Array, " width"]], Float[Array, " width"]
        ] = lambda x: x,
        output_activation: Callable[
            [Float[Array, " width"]], Float[Array, " width"]
        ] = jnn.relu,
        output_final_activation: Callable[
            [Float[Array, " width"]], Float[Array, " width"]
        ] = lambda x: x,
        *,
        solver: type[diffrax.AbstractSolver] = diffrax.Tsit5,
        key: Key,
        time_in_input: bool = False,
        inference: bool = True,
        state_size: int = 16,
    ):
        term_key, initial_key, output_key = jr.split(key, 3)

        self.solver = solver
        self.time_in_input = time_in_input

        self.state_size = state_size
        self.inference = inference

        self.in_size = in_size
        self.latent_size = latent_size
        self.out_size = out_size

        self.term = MLPNCDETerm(
            input_size=in_size,
            data_size=latent_size,
            width_size=width_size,
            depth=depth,
            key=term_key,
            add_time=time_in_input,
            activation=field_activation,
            final_activation=field_final_activation,
        )

        self.initial = eqx.nn.MLP(
            in_size=in_size + int(time_in_input),
            out_size=latent_size,
            width_size=width_size,
            depth=depth,
            key=initial_key,
            activation=initial_state_activation,
            final_activation=initial_state_final_activation,
        )

        self.output = eqx.nn.MLP(
            in_size=latent_size,
            out_size=out_size,
            width_size=width_size,
            depth=depth,
            key=output_key,
            activation=output_activation,
            final_activation=output_final_activation,
        )

        self.state_index = eqx.nn.StateIndex(self.empty_state())
