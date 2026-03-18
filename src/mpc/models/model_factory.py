from .experimental_models import CartPoleModel, TwoWheeledModel, NonlinearSampleSystemModel, FirstOrderLagModel
from .composite_models import GreenhouseCompositeModel


def create_model(args, config):
    """
    Mapping string names to Class objects
    REFERENCES:
        - https://www.freecodecamp.org/news/how-to-use-the-factory-pattern-in-python-a-practical-guide/
        - https://dev.to/dentedlogic/stop-writing-giant-if-else-chains-master-the-python-registry-pattern-ldm
    TODO:
        - Decorator registry method as showing in dev.to
    """
    model_map = {
        "FirstOrderLag": FirstOrderLagModel,
        "TwoWheeledConst": TwoWheeledModel,
        "TwoWheeledTrack": TwoWheeledModel,
        "CartPole": CartPoleModel,
        "NonlinearSample": NonlinearSampleSystemModel,
        "Greenhouse": GreenhouseCompositeModel,
    }

    model_type = args.env
    model_class = model_map.get(model_type)

    if not model_class:
        raise ValueError(f"No model found for type: {model_type}")

    # Initialize and return the specific model
    return model_class(config)
