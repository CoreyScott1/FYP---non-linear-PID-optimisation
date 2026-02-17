from model import PIDController 
from swarm import agent_swarm
from paramDisplay import *
import numpy as np
import math


def swarm_optimisation():
    swarm = agent_swarm(no_of_agents=10)
    iterations = 50

    for i in range(iterations):
        print(f"Iteration {i+1}/{iterations}")
        swarm.update_fitness()
        swarm.update_positions()


def sample_use():
    force_values = []
    angles = []
    time_limit = 10.0  # seconds
    
    # Create PID controller and run simulation
    pid_controller = PIDController(Kp=10.0, Ki=10.0, Kd=8.0, gamma=0.4, mu=0.7, setpoint=2*np.pi/3)
    velocity_history, position_history, set_points = pid_controller.sim_run(time_limit,control_enabled=True)
    
    # Plot velocity and position history
    plot_velocity_position_history(velocity_history, position_history, time_limit)

    xPos = [pid_controller.physical_params["l"] * math.cos(angle) for angle in position_history]
    yPos = [pid_controller.physical_params["l"] * math.sin(angle) for angle in position_history]
    set_points_x = [pid_controller.physical_params["l"] * math.cos(angle) for angle in set_points]
    set_points_y = [pid_controller.physical_params["l"] * math.sin(angle) for angle in set_points]

    # Create and display animation
    create_animation(pid_controller, xPos, yPos, set_points_x, set_points_y)

if __name__ == "__main__":
    swarm = agent_swarm(no_of_agents=10)
    iterations = 20

    pid_controller = PIDController(setpoint=2*math.pi/3)
    show_animation = True


    for i in range(iterations):
        print(f"Iteration {i+1}/{iterations}")
        swarm.update_positions()
        print(f"Best Agent Fitness: {swarm.get_best_agent().fitness}")
        print(f"Best Agent Parameters: {swarm.get_best_agent().values}")
        if show_animation:
            pid_controller.set_PID_params(*swarm.get_best_agent().values)
            velocity_history, position_history, set_points = pid_controller.sim_run(time_limit=10.0, control_enabled=True)


            xPos = [pid_controller.physical_params["l"] * math.cos(angle) for angle in position_history]
            yPos = [pid_controller.physical_params["l"] * math.sin(angle) for angle in position_history]
            set_points_x = [pid_controller.physical_params["l"] * math.cos(angle) for angle in set_points]
            set_points_y = [pid_controller.physical_params["l"] * math.sin(angle) for angle in set_points]

            create_animation(pid_controller.physical_params, pid_controller.running_params, xPos, yPos, set_points_x, set_points_y)


    agent_list = swarm.get_swarm_values()


    
    # Transpose agent_list to get parameters as rows instead of columns
    param_array = list(map(list, zip(*agent_list)))

    print(param_array)

    ranges = [(0, 20), (0, 20), (0, 20), (0, 1), (0, 1)]

    for x in enumerate(param_array):
        print(f"Parameter Set {x[0]+1}: {x[1]}")

    plot_all_params(param_array[:-1], x_ranges=ranges)
    agent_history = swarm.get_agent_histories()
    
    # Restructure from agents -> frames -> (parameters, fitness) to frames -> parameters -> agent values
    num_frames = len(agent_history[0]) if agent_history else 0
    num_params = len(agent_history[0][0][0]) if agent_history and agent_history[0] else 0
    formatted_histories = [
        [[agent[frame_idx][0][param_idx] for agent in agent_history] for param_idx in range(num_params)]
        for frame_idx in range(num_frames)
    ]


    animate_number_line(formatted_histories, ranges, 500)
    