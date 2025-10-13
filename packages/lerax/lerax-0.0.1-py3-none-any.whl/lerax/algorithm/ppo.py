from __future__ import annotations

import equinox as eqx
import jax
import optax
from jax import numpy as jnp
from jax import random as jr
from jaxtyping import Array, Float, Key, Scalar

from lerax.buffer import RolloutBuffer
from lerax.env import AbstractEnvLike
from lerax.policy import AbstractActorCriticPolicy
from lerax.utils import filter_scan

from .on_policy import AbstractOnPolicyAlgorithm


class PPOStats(eqx.Module):
    approx_kl: Float[Array, ""]
    total_loss: Float[Array, ""]
    policy_loss: Float[Array, ""]
    value_loss: Float[Array, ""]
    entropy_loss: Float[Array, ""]
    state_magnitude_loss: Float[Array, ""]


class PPO[ActType, ObsType](AbstractOnPolicyAlgorithm[ActType, ObsType]):
    """Proximal Policy Optimization (PPO) algorithm."""

    env: AbstractEnvLike[ActType, ObsType]
    policy: AbstractActorCriticPolicy[Float, ActType, ObsType]
    optimizer: eqx.AbstractVar[optax.GradientTransformation]
    opt_state_index: eqx.AbstractVar[eqx.nn.StateIndex[optax.OptState]]

    clipper: optax.GradientTransformation
    clipper_index: eqx.nn.StateIndex

    gae_lambda: float = eqx.field(static=True)
    gamma: float = eqx.field(static=True)
    num_steps: int = eqx.field(static=True)
    batch_size: int = eqx.field(static=True)

    num_epochs: int = eqx.field(static=True)
    num_mini_batches: int = eqx.field(static=True)

    normalize_advantages: bool = eqx.field(static=True)
    clip_coefficient: float = eqx.field(static=True)
    clip_value_loss: bool = eqx.field(static=True)
    entropy_loss_coefficient: float = eqx.field(static=True)
    value_loss_coefficient: float = eqx.field(static=True)
    state_magnitude_coefficient: float = eqx.field(static=True)
    max_grad_norm: float = eqx.field(static=True)

    def __init__(
        self,
        env: AbstractEnvLike[ActType, ObsType],
        policy: AbstractActorCriticPolicy[Float, ActType, ObsType],
        *,
        num_steps: int = 2048,
        num_epochs: int = 16,
        num_batches: int = 32,
        gae_lambda: float = 0.95,
        gamma: float = 0.99,
        clip_coefficient: float = 0.2,
        clip_value_loss: bool = False,
        entropy_loss_coefficient: float = 0.0,
        value_loss_coefficient: float = 0.5,
        state_magnitude_coefficient: float = 0.0,
        max_grad_norm: float = 0.5,
        normalize_advantages: bool = True,
    ):
        self.env = env
        self.policy = policy

        self.num_steps = int(num_steps)
        self.num_epochs = int(num_epochs)
        self.num_mini_batches = int(num_batches)
        self.batch_size = self.num_steps // self.num_mini_batches

        self.gae_lambda = float(gae_lambda)
        self.gamma = float(gamma)

        self.clip_coefficient = float(clip_coefficient)
        self.clip_value_loss = bool(clip_value_loss)
        self.entropy_loss_coefficient = float(entropy_loss_coefficient)
        self.value_loss_coefficient = float(value_loss_coefficient)
        self.state_magnitude_coefficient = float(state_magnitude_coefficient)
        self.max_grad_norm = float(max_grad_norm)
        self.normalize_advantages = bool(normalize_advantages)

        # Keep optimizer and clipper separate to allow defining the optimizer
        # somewhere else in the future
        self.clipper = optax.clip_by_global_norm(self.max_grad_norm)
        clipper_state = self.clipper.init(eqx.filter(policy, eqx.is_inexact_array))
        self.clipper_index = eqx.nn.StateIndex(clipper_state)

        self.optimizer = optax.inject_hyperparams(optax.adam)(3e-4)
        opt_state = self.optimizer.init(eqx.filter(policy, eqx.is_inexact_array))
        self.opt_state_index = eqx.nn.StateIndex(opt_state)

    @staticmethod
    def ppo_loss(
        policy: AbstractActorCriticPolicy[Float, ActType, ObsType],
        rollout_buffer: RolloutBuffer[ActType, ObsType],
        normalize_advantages: bool,
        clip_coefficient: float,
        clip_value_loss: bool,
        value_loss_coefficient: float,
        state_magnitude_coefficient: float,
        entropy_loss_coefficient: float,
    ) -> tuple[Float[Array, ""], PPOStats]:
        _, values, log_probs, entropy = jax.vmap(policy.evaluate_action)(
            rollout_buffer.states, rollout_buffer.observations, rollout_buffer.actions
        )

        log_ratios = log_probs - rollout_buffer.log_probs
        ratios = jnp.exp(log_ratios)
        approx_kl = jnp.mean(ratios - log_ratios) - 1

        advantages = rollout_buffer.advantages
        if normalize_advantages:
            advantages = (advantages - jnp.mean(advantages)) / (
                jnp.std(advantages) + jnp.finfo(advantages.dtype).eps
            )

        policy_loss = -jnp.mean(
            jnp.minimum(
                advantages * ratios,
                advantages
                * jnp.clip(ratios, 1 - clip_coefficient, 1 + clip_coefficient),
            )
        )

        if clip_value_loss:
            clipped_values = rollout_buffer.values + jnp.clip(
                values - rollout_buffer.values,
                -clip_coefficient,
                clip_coefficient,
            )
            value_loss = (
                jnp.mean(
                    jnp.minimum(
                        jnp.square(values - rollout_buffer.returns),
                        jnp.square(clipped_values - rollout_buffer.returns),
                    )
                )
                / 2
            )
        else:
            value_loss = jnp.mean(jnp.square(values - rollout_buffer.returns)) / 2

        entropy_loss = -jnp.mean(entropy)

        # TODO: Add state magnitude loss
        # State loss is proportional to the squared norm of the latent state of the policy
        state_magnitude_loss = jnp.array(0.0)

        loss = (
            policy_loss
            + value_loss * value_loss_coefficient
            + state_magnitude_loss * state_magnitude_coefficient
            + entropy_loss * entropy_loss_coefficient
        )

        return loss, PPOStats(
            approx_kl,
            loss,
            policy_loss,
            value_loss,
            entropy_loss,
            state_magnitude_loss,
        )

    ppo_loss_grad = staticmethod(eqx.filter_value_and_grad(ppo_loss, has_aux=True))

    def train_batch(
        self,
        state: eqx.nn.State,
        policy: AbstractActorCriticPolicy[Float, ActType, ObsType],
        rollout_buffer: RolloutBuffer[ActType, ObsType],
    ) -> tuple[
        eqx.nn.State, AbstractActorCriticPolicy[Float, ActType, ObsType], PPOStats
    ]:
        """
        Train the policy for one batch using the rollout buffer.

        Assumes that the rollout buffer is a single batch of data.
        """
        (_, stats), grads = self.ppo_loss_grad(
            policy,
            rollout_buffer,
            self.normalize_advantages,
            self.clip_coefficient,
            self.clip_value_loss,
            self.value_loss_coefficient,
            self.state_magnitude_coefficient,
            self.entropy_loss_coefficient,
        )

        clipper_state = state.get(self.clipper_index)
        updates, clipper_state = self.clipper.update(grads, clipper_state)
        state = state.set(self.clipper_index, clipper_state)

        opt_state = state.get(self.opt_state_index)

        updates, new_opt_state = self.optimizer.update(updates, opt_state)
        state = state.set(self.opt_state_index, new_opt_state)

        policy = eqx.apply_updates(policy, updates)

        return state, policy, stats

    def train_epoch(
        self,
        state: eqx.nn.State,
        policy: AbstractActorCriticPolicy[Float, ActType, ObsType],
        rollout_buffer: RolloutBuffer[ActType, ObsType],
        *,
        key: Key,
    ):
        """
        Train the policy for one epoch using the rollout buffer.

        One epoch consists of multiple mini-batches.
        """

        def batch_scan(
            carry: tuple[
                eqx.nn.State, AbstractActorCriticPolicy[Float, ActType, ObsType]
            ],
            rollout_buffer: RolloutBuffer[ActType, ObsType],
        ) -> tuple[
            tuple[eqx.nn.State, AbstractActorCriticPolicy[Float, ActType, ObsType]],
            PPOStats,
        ]:
            state, policy = carry
            state, policy, stats = self.train_batch(state, policy, rollout_buffer)
            return (state, policy), stats

        (state, policy), stats = filter_scan(
            batch_scan,
            (state, policy),
            rollout_buffer.batches(self.batch_size, key=key),
        )

        stats = jax.tree.map(jnp.mean, stats)

        return state, policy, stats

    @staticmethod
    def explained_variance(
        returns: Float[Array, ""], values: Float[Array, ""]
    ) -> Float[Array, ""]:
        variance = jnp.var(returns)
        explained_variance = 1 - jnp.var(returns - values) / (
            variance + jnp.finfo(returns.dtype).eps
        )
        return explained_variance

    def train(
        self,
        state: eqx.nn.State,
        policy: AbstractActorCriticPolicy[Float, ActType, ObsType],
        rollout_buffer: RolloutBuffer[ActType, ObsType],
        *,
        key: Key,
    ) -> tuple[
        eqx.nn.State,
        AbstractActorCriticPolicy[Float, ActType, ObsType],
        dict[str, Scalar],
    ]:
        def epoch_scan(
            carry: tuple[
                eqx.nn.State, AbstractActorCriticPolicy[Float, ActType, ObsType], Key
            ],
            _,
        ) -> tuple[
            tuple[
                eqx.nn.State, AbstractActorCriticPolicy[Float, ActType, ObsType], Key
            ],
            PPOStats,
        ]:
            state, policy, key = carry
            epoch_key, carry_key = jr.split(key, 2)
            state, policy, stats = self.train_epoch(
                state, policy, rollout_buffer, key=epoch_key
            )
            return (state, policy, carry_key), stats

        (state, policy, _), stats = filter_scan(
            epoch_scan, (state, policy, key), length=self.num_epochs
        )

        stats = jax.tree.map(jnp.mean, stats)
        explained_variance = self.explained_variance(
            rollout_buffer.returns, rollout_buffer.values
        )
        log = {
            "approx_kl": stats.approx_kl,
            "loss": stats.total_loss,
            "policy_loss": stats.policy_loss,
            "value_loss": stats.value_loss,
            "entropy_loss": stats.entropy_loss,
            "state_magnitude_loss": stats.state_magnitude_loss,
            "explained_variance": explained_variance,
        }

        return state, policy, log

    @classmethod
    def load(cls, path: str) -> PPO[ActType, ObsType]:
        raise NotImplementedError

    def save(self, path: str) -> None:
        raise NotImplementedError
