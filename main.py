from model import PIDController 
from swarm import agent_swarm
from paramDisplay import *
import numpy as np
import math
import save


def sim_test():
    force_values = []
    angles = []
    time_limit = 10.0  # seconds
    
    # Create PID controller and run simulation
    pid_controller = PIDController(setpoint=2*np.pi/3)
    pid_controller.set_PID_params(P=2.0, I=0.5, D=1.0, gamma=1, mu=1)
    velocity_history, position_history, set_points = pid_controller.sim_run(time_limit,control_enabled=True)

    for velocity, position in zip(velocity_history, position_history):
        print(f"Velocity: {velocity:.2f}, Position: {position:.2f}")
    
    # Plot velocity and position history
    plot_velocity_position_history(velocity_history, position_history, time_limit)

    xPos = [pid_controller.physical_params["l"] * math.cos(angle) for angle in position_history]
    yPos = [pid_controller.physical_params["l"] * math.sin(angle) for angle in position_history]
    set_points_x = [pid_controller.physical_params["l"] * math.cos(angle) for angle in set_points]
    set_points_y = [pid_controller.physical_params["l"] * math.sin(angle) for angle in set_points]

    # Create and display animation
    create_animation(pid_controller.physical_params, pid_controller.running_params, xPos, yPos, set_points_x, set_points_y)



def swarm_optimisation():
    swarm = agent_swarm(no_of_agents=15)
    iterations = 30

    pid_controller = PIDController(setpoint=2*math.pi/3)
    show_animation = False


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
    

    save.save_swarm_state(swarm, iterations, "final_swarm_state.yaml")
    print("Optimization Complete!")
    best_agent = swarm.get_best_agent()

    print(f"Best Agent Fitness: {best_agent.fitness}")
    print(f"Best Agent Parameters: {best_agent.values}")
    

    best_historical_agent = max(swarm.agents, key=lambda agent: max(fitness for _, fitness in agent.History))

                                                
    pid_controller.set_PID_params(*best_historical_agent.values)
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

    ranges = [(0, 50), (0, 50), (0, 50), (0, 1), (0, 1)]

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
    

if __name__ == "__main__":
    # sample_use()
    #sim_test()
    swarm_optimisation()

