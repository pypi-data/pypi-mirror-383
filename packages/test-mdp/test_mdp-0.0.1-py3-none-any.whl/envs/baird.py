'''
Baird's counterexample environment
'''
from typing import Tuple

import numpy as np
from nptyping import NDArray

from envs.base_mdp import BaseMDP
from utils.math_utils import rowwise_kron, compute_stationary_dist

class Baird(BaseMDP):

    NUM_STATES = 7
    NUM_ACTIONS = 2
    num_features = 8

    DASH = 0 
    SOLID = 1

    def __init__(self, gamma:float=0.9):

        self.gamma = gamma
        self.current_state = None
        self.num_steps = 0

        self.phi = self.construct_feature()
        self.pi_beta, self.pi_target = self.construct_target_behavior_policy()
        self.transition_mat = self.construct_transition()

        self.p_pi = self.pi_target@self.transition_mat
        self.p_beta = self.pi_beta@self.transition_mat
        self.d_mu = np.diag(compute_stationary_dist(self.p_beta))


        self.rewards = self.construct_reward()
        self.expected_rewards = np.sum(self.p_pi*self.rewards, axis=1)


        self.proj = self.phi @ np.linalg.pinv(self.phi.T@self.d_mu@self.phi) @ self.phi.T @ self.d_mu


        self.sol = np.linalg.pinv(self.phi.T @ self.d_mu @ (np.eye(self.NUM_STATES) - self.gamma*self.p_pi) @ self.phi) @ (self.phi.T @ self.d_mu @ self.expected_rewards)


    def construct_reward(self)->NDArray:
        '''Construct reward matrix'''
        self.rewards = np.zeros((self.NUM_STATES, self.NUM_STATES))
        return self.rewards


    def construct_target_behavior_policy(self)->Tuple[NDArray, NDArray]:
        '''Construct target and behavior policy'''
        self.target_policy = np.array([0, 1])
        self.behavior_policy = np.array([1/6, 5/6])
        self.target_policy = np.tile(self.target_policy, (self.NUM_STATES, 1))
        self.behavior_policy = np.tile(self.behavior_policy, (self.NUM_STATES, 1))
        self.pi_begta = rowwise_kron(np.eye(self.NUM_STATES), self.behavior_policy)
        self.pi_target = rowwise_kron(np.eye(self.NUM_STATES), self.target_policy)

        return self.pi_begta, self.pi_target

    def construct_transition(self)->NDArray: 
        '''Construct transition matrix size of SA times S'''
        self.transition_mat = np.zeros((self.NUM_STATES*self.NUM_ACTIONS, self.NUM_STATES))
        for s in range(0, self.NUM_STATES):
            self.transition_mat[s*self.NUM_ACTIONS + self.SOLID, -1] = 1.0
            self.transition_mat[s*self.NUM_ACTIONS + self.DASH, :-1] = 1/6
        return self.transition_mat
               
    def construct_feature(self,)->NDArray:
        '''Construct baird feature matrix'''
        self.phi = np.zeros((self.NUM_STATES, self.num_features))
        for s in range(self.NUM_STATES):
            self.phi[s,s] = 2
            self.phi[s,-1 ] = 1
        self.phi[-1,-1] = 2
        self.phi[-1, -2] = 1
        return self.phi
    

    def reset(self)->Tuple[NDArray,dict]:
        '''Return initial state'''

        state = np.random.randint(0, self.NUM_STATES)
        self.num_steps = 0

        current_phi = self.phi[state,:]
        self.current_state = state

        info = {'rho': 0} # null value

        return state, current_phi, info

    def sample_action(self, state=None)->int:
        '''Select action according to behavior policy'''

        action = np.random.choice(np.arange(self.NUM_ACTIONS), 1, p=self.behavior_policy[state,:])[0]
        return action

    def step(self, state:int, action:int)->Tuple[NDArray,float,bool,bool,dict]:
        '''Take action, return next state, reward, done, truncated, info'''
        done = False
        truncated = False 
        self.num_steps += 1

        next_state = np.random.choice(np.arange(self.NUM_STATES), p=self.transition_mat[state*self.NUM_ACTIONS+action,:])
        next_phi = self.phi[next_state,:]
        reward = self.rewards[state, next_state]
        
        info = {'rho':self.target_policy[state,action]/self.behavior_policy[state, action]}  

        self.current_state = next_state
        return next_state, next_phi, reward, done, truncated, info
    
    
    def get_bellman_error(self, weight: np.ndarray) -> float:
        be = self.proj @ (self.expected_rewards + self.gamma*self.p_pi @ self.phi @ weight - self.phi @ weight)
        return np.linalg.norm(np.sqrt(self.d_mu)@be)
    
    def get_error(self, weight)->float:
        error = np.linalg.norm(weight - self.sol )
        return error

    