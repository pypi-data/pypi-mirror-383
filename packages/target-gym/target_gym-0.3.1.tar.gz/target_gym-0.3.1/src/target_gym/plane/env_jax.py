import time
from typing import Callable

import chex
import jax
import jax.numpy as jnp
from gymnax.environments import environment, spaces

from target_gym.plane.env import (
    EnvMetrics,
    PlaneParams,
    PlaneState,
    check_is_terminal,
    compute_next_state,
    compute_reward,
    get_obs,
)
from target_gym.plane.rendering import _render
from target_gym.utils import compute_norm_from_coordinates, save_video


class Airplane2D(environment.Environment[PlaneState, PlaneParams]):
    """
    JAX-compatible 2D airplane environment.
    """

    render_plane = classmethod(_render)
    screen_width = 600
    screen_height = 400

    def __init__(self, integration_method: str = "rk4_1"):
        self.obs_shape = (9,)
        self.positions_history = []
        self.integration_method = integration_method

    @property
    def default_params(self) -> PlaneParams:
        return PlaneParams()

    def compute_reward(self, state, params):
        return compute_reward(state, params)

    def step_env(
        self,
        key: chex.PRNGKey,
        state: PlaneState,
        action: jnp.ndarray,
        params: PlaneParams = None,
    ):
        """
        Performs step transitions using JAX, returns observation, new state, reward, done, info
        """
        if params is None:
            params = self.default_params

        power, stick = action
        power = (power + 1) / 2  # map from [-1, 1] to [0, 1]
        stick = jnp.deg2rad(stick * 15)  # radians

        new_state, metrics = compute_next_state(
            power, stick, state, params, integration_method=self.integration_method
        )
        reward = self.compute_reward(new_state, params)
        terminated, truncated = check_is_terminal(new_state, params, xp=jnp)
        done = terminated | truncated

        obs = self.get_obs(new_state)
        return (
            obs,
            new_state,
            reward,
            done,
            {"metrics": metrics, "last_state": new_state},
        )

    def is_terminal(self, state: PlaneState, params: PlaneParams) -> jax.Array:
        return check_is_terminal(state, params, xp=jnp)

    def reset_env(self, key: chex.PRNGKey, params: PlaneParams = None):
        """
        Reset the environment using JAX random keys
        """
        if params is None:
            params = PlaneParams(max_steps_in_episode=Airplane2D.max_steps)
        key, altitude_key, target_key = jax.random.split(key, 3)

        initial_x = 0.0
        initial_z = jax.random.uniform(
            altitude_key,
            minval=params.initial_altitude_range[0],
            maxval=params.initial_altitude_range[1],
        )
        initial_z_dot = params.initial_z_dot
        initial_x_dot = params.initial_x_dot
        initial_theta = jnp.deg2rad(params.initial_theta)
        initial_gamma = jnp.arcsin(
            initial_z_dot
            / (
                compute_norm_from_coordinates(
                    jnp.array([initial_x_dot, initial_z_dot + 1e-6])
                )
            )
        )
        initial_alpha = initial_theta - initial_gamma
        initial_m = params.initial_mass + params.initial_fuel_quantity
        initial_power = params.initial_power
        initial_stick = jnp.deg2rad(params.initial_stick)
        initial_fuel = params.initial_fuel_quantity

        target_altitude = jax.random.uniform(
            target_key,
            minval=params.target_altitude_range[0],
            maxval=params.target_altitude_range[1],
        )

        state = PlaneState(
            x=initial_x,
            x_dot=initial_x_dot,
            z=initial_z,
            z_dot=initial_z_dot,
            theta=initial_theta,
            theta_dot=jnp.deg2rad(params.initial_theta_dot),
            alpha=initial_alpha,
            gamma=initial_gamma,
            m=initial_m,
            power=initial_power,
            stick=initial_stick,
            fuel=initial_fuel,
            time=0,
            target_altitude=target_altitude,
        )

        obs = self.get_obs(state)
        return obs, state

    def get_obs(self, state: PlaneState):
        """
        Observation vector
        """
        return get_obs(state, xp=jnp)

    def render(self, screen, state: PlaneState, params: PlaneParams, frames, clock):
        """
        JAX-compatible rendering wrapper
        """
        frames, screen, clock = self.render_plane(screen, state, params, frames, clock)
        return frames, screen, clock

    def save_video(
        self,
        select_action: Callable[[jnp.ndarray], jnp.ndarray],
        seed: int,
        params=None,
        folder="videos",
        episode_index=0,
        FPS=60,
        format="mp4",
        save_trajectory: bool = False,
    ):
        return save_video(
            self,
            select_action,
            folder,
            episode_index,
            FPS,
            params,
            seed=seed,
            format=format,
            save_trajectory=save_trajectory,
        )

    def action_space(self, params: PlaneParams | None = None) -> spaces.Discrete:
        """Action space of the environment."""
        return spaces.Box(
            low=jnp.array([-1.0, -1.0]),
            high=jnp.array([1.0, 1.0]),
            shape=(2,),
            dtype=jnp.float32,
        )

    def observation_space(self, params: PlaneParams) -> spaces.Box:
        """Observation space of the environment."""
        inf = jnp.finfo(jnp.float32).max
        return spaces.Box(-inf, inf, self.obs_shape, dtype=jnp.float32)

    def state_space(self, params: PlaneParams) -> spaces.Box:
        """Observation space of the environment."""
        inf = jnp.finfo(jnp.float32).max
        return spaces.Box(
            -inf, inf, len(PlaneState.__class_params__), dtype=jnp.float32
        )


def run_timesteps(key, env, env_params, n_timesteps=10_000, action_type="constant"):
    """Run n_timesteps in the env with constant or random action."""
    # Reset environment
    key_reset, key = jax.random.split(key)
    obs, state = env.reset(key_reset, env_params)

    def step_fn(carry, _):
        obs, state, key = carry
        key, key_step, key_action = jax.random.split(key, 3)

        # Choose action
        if action_type == "constant":
            action = jnp.array([0.8, 0.0])
        else:  # random
            action = jax.random.uniform(key_action, (2,), minval=-1.0, maxval=1.0)

        # Step environment
        next_obs, next_state, reward, done, _ = env.step(
            key_step, state, action, env_params
        )

        carry = (next_obs, next_state, key)
        return carry, (reward, done)

    # Rollout with lax.scan
    (_, _, _), (rewards, dones) = jax.lax.scan(
        step_fn, (obs, state, key), xs=None, length=n_timesteps
    )
    return rewards, dones


# JIT-compiled version
run_timesteps_jit = jax.jit(run_timesteps, static_argnums=(1, 2, 3, 4))

if __name__ == "__main__":
    env = Airplane2D()
    seed = 42

    env_params = PlaneParams(
        max_steps_in_episode=1_000,
        target_altitude_range=(5000, 5000),
        initial_altitude_range=(5000, 5000),
    )
    action = (0.5, 0.0)
    env.save_video(
        lambda o: action,
        seed,
        folder="videos",
        episode_index=0,
        params=env_params,
        format="gif",
        save_trajectory=True,
    )

    # import time

    # import numpy as np

    # # Benchmark parameters
    # env = Airplane2D()
    # env_params = PlaneParams(max_steps_in_episode=10_000)

    # print("---- Constant action ----")
    # benchmark(
    #     env, env_params, n_timesteps=100_000, n_episodes=10, action_type="constant"
    # )

    # print("\n---- Random action ----")
    # benchmark(env, env_params, n_timesteps=100_000, n_episodes=10, action_type="random")
