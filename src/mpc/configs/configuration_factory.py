from .experimental_configurations import CartPoleConfigModule, TwoWheeledConfigModule, NonlinearSampleSystemConfigModule, FirstOrderLagConfigModule, NonlinearSampleSystemExtendConfigModule

def create_configuration(args):
    """
    Mapping string names to Class objects
    REFERENCES:
        - https://www.freecodecamp.org/news/how-to-use-the-factory-pattern-in-python-a-practical-guide/
        - https://dev.to/dentedlogic/stop-writing-giant-if-else-chains-master-the-python-registry-pattern-ldm
    TODO:
        - Decorator registry method as showing in dev.to
    """
    model_map = {
        "CartPoleConfigModule": CartPoleConfigModule,
        "TwoWheeledConfigModule": TwoWheeledConfigModule,
        "NonlinearSampleSystemConfigModule": NonlinearSampleSystemConfigModule,
        "FirstOrderLagConfigModule": FirstOrderLagConfigModule,
        "NonlinearSampleSystemExtendConfigModule": NonlinearSampleSystemExtendConfigModule
    }

    configuration_type = args.configuration_type
    configuration_class = model_map.get(configuration_type)

    if not configuration_class:
        raise ValueError(f"No configuration found for type: {configuration_type}")

    # Initialize and return the specific configuration
    return configuration_class()
