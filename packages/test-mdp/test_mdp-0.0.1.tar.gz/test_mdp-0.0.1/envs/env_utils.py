'''
  utils related to environments
'''


def get_env(name:str, **kwargs):
    if name == "Baird":
        from envs.baird import Baird
        return Baird(kwargs.get('gamma', 0.9))
    elif name == "RandomWalkTabular":
        from envs.random_walk_tabular import RandomWalkTabular
        return RandomWalkTabular(gamma=kwargs.get('gamma', 0.9))
    elif name == "RandomWalkDependent":
        from envs.random_walk_dependent import RandomWalkDependent
        return RandomWalkDependent(gamma=kwargs.get('gamma', 0.9))
    else:
        raise NotImplementedError(f"Environment {name} not implemented")