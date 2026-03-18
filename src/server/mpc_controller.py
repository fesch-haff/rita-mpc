import os

from ..mpc import controllers
from ..mpc.planners import create_planner
from ..mpc.controllers import create_controller

class MPCController:
    def __init__(self, arguments):
        # Load configuration
        self.config, self.predictors = self.load_config()

        # Initialize components
        planner = create_planner(arguments, self.config)
        self.model = GreenhouseCompositeModel(self.predictors, self.config)
        self.controller = create_controller(arguments, self.config, sel)



        self.controller = BruteForce(self.config, self.model)
        self.runner = LiveRunner(self.controller, self.planner)

    @staticmethod
    def load_config():
        config_path = os.getenv("CONFIG_PATH")
        predictors_path = os.getenv("PREDICTORS_PATH")

        """Load raw config and build control config"""
        config = build_control_config(load_raw_config(config_path))
        predictors = load_boosters(Path(predictors_path))

        return config, predictors

    def run(self):
        state_names = self.config.state_names
        state_goal = self.config.goal_state
        curr_state  = Registry.get_system_states(state_names)

        """Run MPC to get control instructions"""
        u = self.runner.run(curr_state, state_goal)
        return u.tolist()