from .experimental_runners import ExpRunner
from .greenhouse_runner import GreenhouseRunner

def create_runner(args):
    """
    Mapping string names to Class objects
    REFERENCES:
        - https://www.freecodecamp.org/news/how-to-use-the-factory-pattern-in-python-a-practical-guide/
        - https://dev.to/dentedlogic/stop-writing-giant-if-else-chains-master-the-python-registry-pattern-ldm
    TODO:
        - Decorator registry method as showing in dev.to
    """
    runner_map = {
        "ExperimentalRunners": ExpRunner,
        "GreenhouseRunner": GreenhouseRunner,
    }

    runner_type = args.runner_type
    runner_class = runner_map.get(runner_type)

    if not runner_class:
        raise ValueError(f"No runner found for type: {runner_type}")

    # Initialize and return the specific runner
    return runner_class()
