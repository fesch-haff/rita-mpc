from .experiential_environments import FirstOrderLagEnv, TwoWheeledConstEnv, TwoWheeledTrackEnv, CartPoleEnv, NonlinearSampleSystemEnv

def create_environment(args):
    """
    Mapping string names to Class objects
    REFERENCES:
        - https://www.freecodecamp.org/news/how-to-use-the-factory-pattern-in-python-a-practical-guide/
        - https://dev.to/dentedlogic/stop-writing-giant-if-else-chains-master-the-python-registry-pattern-ldm
    TODO:
        - Decorator registry method as showing in dev.to
    """
    environment_map = {
        "FirstOrderLag": FirstOrderLagEnv,
        "TwoWheeledConst": TwoWheeledConstEnv,
        "TwoWheeledTrack": TwoWheeledTrackEnv,
        "CartPole": CartPoleEnv,
        "NonlinearSample": NonlinearSampleSystemEnv,
    }

    environment_type = args.env
    environment_class = environment_map.get(environment_type)

    if not environment_class:
        raise ValueError(f"No environment found for type: {environment_type}")

    # Initialize and return the specific environment
    return environment_class()