from BenchPilotSDK.controller import Controller

# for first run create external network: docker network create -d overlay benchPilot
"""
 This class is the main class fot benchPilot, is a demo of how we can run controller's methods.
"""
if __name__ == '__main__':
    print("Bench Pilot Initialization")

    # Declare your configuration's file name (the default is bench-experiments.yaml):
    
    bench_preferences_file_name = "BenchPilotSDK/conf/bench-experiments.yaml"

    controller = Controller(bench_preferences_file_name)
    controller.start_experiment()
    # controller.start_experiment("storm_x1")
    # controller.get_experiment_timestamps()
    # controller.get_experiment_timestamps("storm_x1")
