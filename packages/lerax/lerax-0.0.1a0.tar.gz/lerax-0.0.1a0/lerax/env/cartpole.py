from __future__ import annotations

from typing import ClassVar, Literal

import equinox as eqx
from jax import numpy as jnp
from jax import random as jr
from jaxtyping import Array, Bool, Float, Int, Key

from lerax.render import AbstractRenderer, Color, PygameRenderer, Transform
from lerax.space import Box, Discrete

from .base_env import AbstractEnv


class SOLVER(eqx.Enumeration):
    explicit = "explicit"
    implicit = "implicit"


class CartPole(AbstractEnv[Int[Array, ""], Float[Array, "4"]]):
    name: ClassVar[str] = "CartPole"

    state_index: eqx.nn.StateIndex[Float[Array, "4"]]
    action_space: Discrete
    observation_space: Box

    gravity: float
    masscart: float
    masspole: float
    total_mass: float
    length: float
    polemass_length: float
    force_mag: float
    tau: float
    solver: SOLVER
    theta_threshold_radians: float
    x_threshold: float

    renderer: AbstractRenderer | None

    def __init__(
        self,
        solver: SOLVER = SOLVER.implicit,
        renderer: AbstractRenderer | Literal["auto"] | None = None,
    ):
        self.gravity = 9.8
        self.masscart = 1.0
        self.masspole = 0.1
        self.total_mass = self.masspole + self.masscart
        self.length = 0.5
        self.polemass_length = self.masspole * self.length
        self.force_mag = 10.0
        self.tau = 0.02
        self.solver = solver

        self.theta_threshold_radians = 12 * 2 * jnp.pi / 360
        self.x_threshold = 2.4

        self.action_space = Discrete(2)
        high = jnp.array(
            [
                self.x_threshold * 2,
                jnp.inf,
                self.theta_threshold_radians * 2,
                jnp.inf,
            ],
        )
        self.observation_space = Box(-high, high)

        self.state_index = eqx.nn.StateIndex(jnp.zeros(4))

        if renderer == "auto":
            self.renderer = self.default_renderer()
        else:
            self.renderer = renderer

    def reset(
        self, state: eqx.nn.State, *, key: Key, low: float = -0.05, high: float = 0.05
    ) -> tuple[eqx.nn.State, Float[Array, "4"], dict]:
        new_state = jr.uniform(key, (4,), minval=low, maxval=high)
        state = state.set(self.state_index, new_state)

        return state, new_state, {}

    def step(self, state: eqx.nn.State, action: Int[Array, ""], *, key: Key) -> tuple[
        eqx.nn.State,
        Float[Array, "4"],
        Float[Array, ""],
        Bool[Array, ""],
        Bool[Array, ""],
        dict,
    ]:
        x, x_dot, theta, theta_dot = state.get(self.state_index)

        force = (action * 2 - 1) * self.force_mag
        costheta = jnp.cos(theta)
        sintheta = jnp.sin(theta)

        temp = (
            force + self.polemass_length * jnp.square(theta_dot) * sintheta
        ) / self.total_mass
        thetaacc = (self.gravity * sintheta - costheta * temp) / (
            self.length
            * (4.0 / 3.0 - self.masspole * jnp.square(costheta) / self.total_mass)
        )
        xacc = temp - self.polemass_length * thetaacc * costheta / self.total_mass

        if self.solver == SOLVER.explicit:
            x = x + self.tau * x_dot
            x_dot = x_dot + self.tau * xacc
            theta = theta + self.tau * theta_dot
            theta_dot = theta_dot + self.tau * thetaacc
        else:
            x_dot = x_dot + self.tau * xacc
            x = x + self.tau * x_dot
            theta_dot = theta_dot + self.tau * thetaacc
            theta = theta + self.tau * theta_dot

        state_vals = jnp.asarray([x, x_dot, theta, theta_dot])
        state = state.set(self.state_index, state_vals)

        within_x = jnp.logical_and(x >= -self.x_threshold, x <= self.x_threshold)
        within_theta = jnp.logical_and(
            theta >= -self.theta_threshold_radians,
            theta <= self.theta_threshold_radians,
        )
        terminated = jnp.logical_not(jnp.logical_and(within_x, within_theta))

        reward = jnp.array(1.0)

        return state, state_vals, reward, terminated, jnp.array(False), {}

    def render(self, state: eqx.nn.State):
        x, _, theta, _ = state.get(self.state_index)
        x = x

        assert self.renderer is not None, "Renderer is not set."
        self.renderer.clear()

        # Ground
        self.renderer.draw_line(
            start=jnp.array((-10.0, 0.0)),
            end=jnp.array((10.0, 0.0)),
            color=Color(0.0, 0.0, 0.0),
            width=0.01,
        )
        # Cart
        cart_w, cart_h = 0.3, 0.15
        cart_col = Color(0.0, 0.0, 0.0)
        self.renderer.draw_rect(jnp.array((x, 0.0)), w=cart_w, h=cart_h, color=cart_col)
        # Pole
        pole_start = jnp.asarray((x, cart_h / 4))
        pole_end = pole_start + self.length * jnp.asarray(
            [jnp.sin(theta), jnp.cos(theta)]
        )
        pole_col = Color(0.8, 0.6, 0.4)
        self.renderer.draw_line(pole_start, pole_end, color=pole_col, width=0.05)
        # Pole Hinge
        hinge_r = 0.025
        hinge_col = Color(0.5, 0.5, 0.5)
        self.renderer.draw_circle(pole_start, radius=hinge_r, color=hinge_col)

        self.renderer.render()

    def default_renderer(self) -> AbstractRenderer:
        width, height = 800, 450
        transform = Transform(
            scale=200.0,
            offset=jnp.array([width / 2, height * 0.1]),
            width=width,
            height=height,
            y_up=True,
        )
        return PygameRenderer(
            width=width,
            height=height,
            background_color=Color(1.0, 1.0, 1.0),
            transform=transform,
        )

    def close(self):
        pass
