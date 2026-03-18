from .derivative_free_controllers import CEM, MPPI, MPPIWilliams, RandomShooting, BruteForce
from .gradient_based_controllers import DDP, iLQR, NMPC, NMPCCGMRES
from .optimization_based_controllers import LinearMPC


def create_controller(args, config, model):
    """
    Mapping string names to Class objects
    REFERENCES:
        - https://www.freecodecamp.org/news/how-to-use-the-factory-pattern-in-python-a-practical-guide/
        - https://dev.to/dentedlogic/stop-writing-giant-if-else-chains-master-the-python-registry-pattern-ldm
    TODO:
        - Decorator registry method as showing in dev.to
    """
    controller_map = {
        "MPC": LinearMPC,
        "CEM": CEM,
        "Random": RandomShooting,
        "MPPI": MPPI,
        "MPPIWilliams": MPPIWilliams,
        "iLQR": iLQR,
        "DDP": DDP,
        "NMPC": NMPC,
        "NMPCCGMRES": NMPCCGMRES,
        "BruteForce": BruteForce,
    }

    controller_type = args.controller_type
    controller_class = controller_map.get(controller_type)

    if not controller_class:
        raise ValueError(f"No controller found for type: {controller_type}")

    # Initialize and return the specific controller
    return controller_class(config, model)