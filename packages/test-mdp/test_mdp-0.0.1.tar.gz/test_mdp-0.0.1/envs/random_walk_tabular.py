import numpy as np
from nptyping import NDArray
from typing import Tuple

from envs.base_mdp import BaseMDP
from utils.math_utils import rowwise_kron, compute_stationary_dist

class RandomWalkTabular(BaseMDP):

    NUM_STATES = 7
    NUM_ACTIONS = 2
    num_features = 7

    LEFT = 0 
    RIGHT = 1

    END_0 = 0
    END_1 = NUM_STATES-1
    START = int((NUM_STATES-1)/2)

    def __init__(self, gamma:float):

        self.gamma = gamma
        self.reward = 0
        self.current_state = None
        self.num_steps = 0
        self.phi = self.construct_feature()


        self.target_policy = np.array([0.4, 0.6])
        self.behavior_policy = np.array([0.5, 0.5])
        self.target_policy = np.tile(self.target_policy, (self.NUM_STATES, 1))
        self.behavior_policy = np.tile(self.behavior_policy, (self.NUM_STATES, 1))

        self.pi_beta , self.pi_target = self.construct_target_behavior_policy()
        self.transition_mat = self.construct_transition()
        
        self.p_pi = self.pi_target@self.transition_mat
        self.p_beta = self.pi_beta@self.transition_mat
        self.d_mu = np.diag(compute_stationary_dist(self.p_beta))


        self.rewards = self.construct_reward()
        self.expected_rewards = np.sum(self.p_pi*self.rewards, axis=1)
        
        self.proj = self.phi @ np.linalg.pinv(self.phi.T@self.d_mu@self.phi) @ self.phi.T @ self.d_mu

        self.sol = np.linalg.pinv(self.phi.T @ self.d_mu @ (np.eye(self.NUM_STATES) - self.gamma*self.p_pi) @ self.phi) @ (self.phi.T @ self.d_mu @ self.expected_rewards)


    def construct_feature(self):
        self.phi = np.eye(self.NUM_STATES)
        return self.phi
    
    def construct_target_behavior_policy(self)->Tuple[NDArray, NDArray]:

        self.target_policy = np.array([0.4, 0.6])
        self.behavior_policy = np.array([0.5, 0.5])
        self.target_policy = np.tile(self.target_policy, (self.NUM_STATES, 1))
        self.behavior_policy = np.tile(self.behavior_policy, (self.NUM_STATES, 1))
        
        self.pi_beta = rowwise_kron(np.eye(self.NUM_STATES), self.behavior_policy)
        self.pi_target = rowwise_kron(np.eye(self.NUM_STATES), self.target_policy)

        return self.pi_beta, self.pi_target
    
    def construct_transition(self):

        self.transition_mat = np.zeros((self.NUM_STATES*self.NUM_ACTIONS, self.NUM_STATES))
        for s in range(1, self.NUM_STATES-1):
            self.transition_mat[s*self.NUM_ACTIONS + self.LEFT, s-1] = 1.0
            self.transition_mat[s*self.NUM_ACTIONS + self.RIGHT, s+1] = 1.0
        self.transition_mat[0, self.START] = 1.0
        self.transition_mat[1, self.START] = 1.0
        self.transition_mat[(self.NUM_STATES-1)*self.NUM_ACTIONS + self.LEFT, self.START] = 1.0
        self.transition_mat[(self.NUM_STATES-1)*self.NUM_ACTIONS + self.RIGHT, self.START] = 1.0

        return self.transition_mat
    def construct_reward(self):
        self.rewards = np.zeros((self.NUM_STATES, self.NUM_STATES))
        self.rewards[self.END_0+1, self.END_0] = -1.0
        self.rewards[self.END_1-1, self.END_1] = 1.0  
        self.expected_rewards = np.sum(self.p_pi*self.rewards, axis=1)
        return self.rewards
    

    def reset(self)->Tuple[NDArray,dict]:
        '''Return initial state'''

        state = np.random.randint(0, self.NUM_STATES)
        self.num_steps = 0

        current_phi = self.phi[state,:]

        info = {'rho':1}

        self.current_state = state
        self.current_phi = current_phi


        return state, current_phi ,info

    def sample_action(self, state=None)->int:
        '''Select action according to behavior policy'''

        action = np.random.choice(np.arange(self.NUM_ACTIONS), 1, p=self.behavior_policy[state,:])[0]
        return action

    def step(self, state:int, action:int)->Tuple[NDArray,float,bool,bool,dict]:

        done = False
        truncated = False 
        self.num_steps += 1
      
      
        next_state = np.random.choice(np.arange(self.NUM_STATES),
                                       p=self.transition_mat[state*self.NUM_ACTIONS+action,:])
        next_phi = self.phi[next_state,:]
        reward = self.rewards[state, next_state]

        info = {'rho':self.target_policy[state, action]/self.behavior_policy[state, action]}
        self.current_state = next_state
        return next_state, next_phi, reward, done, truncated,info
    
    
    def get_bellman_error(self, weight: np.ndarray) -> float:
        be = self.proj @ (self.expected_rewards + self.gamma*self.p_pi @ self.phi @ weight - self.phi @ weight)
        return np.linalg.norm(np.sqrt(self.d_mu)@be)
    
    def get_error(self, weight)->float:
        error = np.linalg.norm(weight - self.sol )
        return error

    