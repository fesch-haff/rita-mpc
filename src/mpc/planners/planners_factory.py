from .experimental_planners import ClosestPointPlanner, ConstantPlanner


def create_planner(args, config):
    """
    Mapping string names to Class objects
    REFERENCES:
        - https://www.freecodecamp.org/news/how-to-use-the-factory-pattern-in-python-a-practical-guide/
        - https://dev.to/dentedlogic/stop-writing-giant-if-else-chains-master-the-python-registry-pattern-ldm
    TODO:
        - Decorator registry method as showing in dev.to
    """
    planner_map = {
        "ConstantPlanner": ConstantPlanner,
        "ClosestPointPlanner": ClosestPointPlanner,
    }

    planner_type = args.planner_type
    planner_class = planner_map.get(planner_type)

    if not planner_class:
        raise ValueError(f"No planner found for type: {planner_type}")

    # Initialize and return the specific planner
    return planner_class(config)
