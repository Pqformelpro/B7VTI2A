# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 16:22:56 2018

@author: Ole
"""

import gym
import retro

import numpy as np

from stable_baselines.common.policies import CnnPolicy
from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines import PPO2

from stable_baselines import logger
from stable_baselines.bench import Monitor
from stable_baselines.common import set_global_seeds

from stable_baselines.common import retro_wrappers

import os


class Discretizer(gym.ActionWrapper):
    
    def __init__(self, env):
        super(Discretizer, self).__init__(env)
        
        buttons = ["B", "A", "MODE", "START", "UP", "DOWN", "LEFT", "RIGHT", "C", "Y", "X", "Z"]
        
        actions = [["LEFT"], ["RIGHT"], ["LEFT", "DOWN"], ["RIGHT", "DOWN"], ["DOWN"], ["DOWN", "B"], ["B"]]
        
        self._actions = []
        
        for action in actions:
            arr = np.array([False] * 12)
            for button in action:
                arr[buttons.index(button)] = True
            self._actions.append(arr)
        self.action_space = gym.spaces.Discrete(len(self._actions))
        
    def action(self, a):
        return self._actions[a].copy()


#############
        
def make_vec_env(env_id, num_env, seed, wrapper_kwargs=None, start_index=0, reward_scale=1.0, gamestate=None):
    if wrapper_kwargs is None:
        wrapper_kwargs = {}

    def make_thunk(rank):
        return lambda: make_env(
            env_id=env_id,
            subrank = rank,
            seed=seed,
            reward_scale=reward_scale,
            gamestate=gamestate,
            wrapper_kwargs=wrapper_kwargs
        )

    set_global_seeds(seed)
    if num_env > 1:
        return SubprocVecEnv([make_thunk(i + start_index) for i in range(num_env)])
    else:
        return DummyVecEnv([make_thunk(start_index)])


def make_env(env_id, subrank=0, seed=None, reward_scale=1.0, gamestate=None, wrapper_kwargs={}):

    gamestate = gamestate or retro.State.DEFAULT
    env = retro_wrappers.make_retro(game=env_id, max_episode_steps=10000, use_restricted_actions=retro.Actions.DISCRETE, state=gamestate)

    env.seed(seed if seed is not None else None)
    env = Monitor(env, logger.get_dir() and os.path.join(logger.get_dir(), str(subrank)), allow_early_resets=True)

    env = retro_wrappers.wrap_deepmind_retro(env, **wrapper_kwargs)

    if reward_scale != 1:
        env = retro_wrappers.RewardScaler(env, reward_scale)

    return env    

############
    

#env = Discretizer(make_retro_env(env_id='SonicTheHedgehog-Genesis', env_state='GreenHillZone.Act1', seed=1234))
env = make_vec_env('SonicTheHedgehog-Genesis', 1, 1234, reward_scale=0.01, gamestate='GreenHillZone.Act1')
#env = DummyVecEnv([lambda: env]) # for i in range(n_cpus)

model = PPO2(CnnPolicy, env, verbose=1, tensorboard_log="./ppo2_sonic_log/")
model.learn(total_timesteps=100000)

obs = env.reset()

while True:
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()