from model import PIDController 
from swarm import agent_swarm
from paramDisplay import *
import numpy as np
import math

# required for saving and loading swarm states
# agent number, agent dimensions, agent values, agent fitness, iteration number
import yaml


def save_swarm_state(swarm, iteration, filename):
        
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
        print(swarm_state)
        # with open(filename, 'w') as file:
        #     yaml.dump(swarm_state, file)

def load_swarm_state(filename):
    with open(filename, 'r') as file:
        swarm_state = yaml.safe_load(file)
    print(swarm_state)

if __name__ == "__main__":
    #sample usage of saving and loading swarm state
    # swarm = agent_swarm(no_of_agents=10)
    # iteration = 5
    # save_swarm_state(swarm, iteration, "swarm_state_10.yaml")


    load_swarm_state("final_swarm_state.yaml")
