'''
Abstract Class for MDP
'''

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any

import numpy as np
from nptyping import NDArray


class BaseMDP(ABC):
    '''
    Base class for Markov Decision Process (MDP) environments.
    
    Subclasses must implement the following methods:
    - reset()
    - step()
    - get_error()
    '''


    @abstractmethod
    def construct_feature(self) -> NDArray:
        '''
        Construct the feature matrix for the MDP.
        
        Returns:
            NDArray: The feature matrix.
        '''
    @abstractmethod
    def construct_transition(self) -> NDArray:
        '''
        Construct the transition matrix for the MDP.
        
        Returns:
            NDArray: The transition matrix.
        '''
    @abstractmethod
    def construct_target_behavior_policy(self) -> Tuple[NDArray, NDArray]:
        '''
        Construct the behavior and target policy matrices.
        
        Returns:
            Tuple[NDArray, NDArray]: The behavior and target policy matrices.
        '''
    
    @abstractmethod
    def reset(self) -> Tuple[int, NDArray, dict]:
        '''
        Resets the environment to an initial state.
        
        Returns:
            Tuple: (state, feature, info)
                - state: The initial state (int).
                - feature: The feature representation of the initial state (NDArray).
                - info: Additional information (dict).
        '''

    @abstractmethod
    def step(self, action: int) -> Tuple[NDArray, float, bool, bool, Dict[str, Any]]:
        '''
        Takes an action and returns the next state, reward, and other information.

        Args:
            action (int): The action taken by the agent.

        Returns:
            Tuple: (next_state, reward, done, truncated, info)
                - next_state: State after the action (NDArray).
                - reward: Reward after the action (float).
                - done: Boolean indicating whether the episode has ended.
                - truncated: Boolean indicating if the episode was truncated.
                - info: Additional information (e.g., importance sampling ratio).
        '''

    
    @abstractmethod
    def get_error(self, weight: np.ndarray) -> float:
        '''
        Calculate the error (e.g., in value function approximation).
        
        Args:
            weight (np.ndarray): The weight parameter (e.g., for value function).

        Returns:
            float: The error based on the weight.
        '''


    @abstractmethod
    def sample_action(self, state: int) -> int:
        '''
        Select an action based on the current state.
        
        Args:
            state (int): The current state.

        Returns:
            int: The action selected by the agent.
        '''
