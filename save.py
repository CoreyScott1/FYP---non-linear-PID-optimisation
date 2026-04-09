from model import PIDController 
from swarm import agent_swarm
from paramDisplay import *
import os
import math

# required for saving and loading swarm states
# agent number, agent dimensions, agent values, agent fitness, iteration number
import yaml


def save_swarm_state(swarm, iteration, filename):
        filename = filename if filename.endswith((".yaml", ".yml")) else f"{filename}.yaml"
        filename = filename if filename.startswith("saves/") else f"saves/{filename}"
        
        range_min = swarm.limit_min
        range_max = swarm.limit_max
        dimension = len(swarm.agents[0].values)

        agent_data = swarm.get_agent_data()


        swarm_state = {
            'iteration': iteration,
            'range_min': range_min,
            'range_max': range_max,
            'dimension': dimension,
            'number_of_agents': len(swarm.agents),
            'agents': agent_data
        }
        #return swarm_state


        with open(filename, 'w') as file:
            yaml.dump(swarm_state, file)

def load_swarm_state(filename):
    with open(f"saves/{filename}", 'r') as file:
        swarm_state = yaml.load(file, Loader=yaml.FullLoader)
    return swarm_state

def get_all_loadable_swarms():

    saves_dir = os.path.join(os.getcwd(), "saves")

    if not os.path.isdir(saves_dir):
        return []  # No saves folder found

    required_keys = {
        'iteration',
        'range_min',
        'range_max',
        'dimension',
        'number_of_agents',
        'agents'
    }

    valid_states = []

    for dirpath, _, filenames in os.walk(saves_dir):
        print(f"Checking directory: {filenames}")
        for filename in filenames:
            if filename.endswith((".yaml", ".yml")):
                file_path = os.path.join(dirpath, filename)

                try:
                    with open(f"saves/{filename}", 'r') as file:
                        swarm_state = yaml.load(file, Loader=yaml.FullLoader)

                    # Validate structure
                    if isinstance(swarm_state, dict) and required_keys.issubset(swarm_state.keys()):
                        if isinstance(swarm_state['agents'], list):
                            valid_states.append(filename)

                except Exception:
                    # Skip invalid or unreadable YAML files

                    continue

    return valid_states
     
    
if __name__ == "__main__":
    # sample usage of saving and loading swarm state
    swarm = agent_swarm(no_of_agents=10)
    iteration = 5
    swarm.update_positions()

    save_swarm_state(swarm, iteration, "swarm_state_10.yaml")

    print(get_all_loadable_swarms())

    print(load_swarm_state("swarm_state_10.yaml"))
