from model import PIDController 
from swarm import agent_swarm
from paramDisplay import *
from CLI import CLI
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
        swarm.update_positions(iteration=i)
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
    
    # Plot sector convergence over iterations
    plot_sector_convergence(swarm, param_names=['P', 'I', 'D', 'Gamma', 'Mu'])
    
    # Restructure from agents -> frames -> (parameters, fitness) to frames -> parameters -> agent values
    num_frames = len(agent_history[0]) if agent_history else 0
    num_params = len(agent_history[0][0][0]) if agent_history and agent_history[0] else 0
    formatted_histories = [
        [[agent[frame_idx][0][param_idx] for agent in agent_history] for param_idx in range(num_params)]
        for frame_idx in range(num_frames)
    ]


    print("Optimization Complete!")
    best_agent = swarm.get_best_agent()

    print(f"Best Agent Fitness: {best_agent.fitness}")
    print(f"Best Agent Parameters: {best_agent.values}")


def optimize(**params):
    swarm = agent_swarm(no_of_agents=params.get("number_of_agents", 15))
    iterations = params.get("iterations", 30)
    show_animation = params.get("show_animation", False)

    pid_controller = PIDController(setpoint=2*math.pi/3)

    for i in range(iterations):
        print(f"Iteration {i+1}/{iterations}")
        swarm.update_positions(iteration=i)
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
        
    print("Optimization Complete!")
    best_agent = swarm.get_best_agent()

    print(f"Best Agent Fitness: {best_agent.fitness}")
    print(f"Best Agent Parameters: {best_agent.values}")

    print("Returning to main menu...")
    return(swarm, i)

    

if __name__ == "__main__":
    #ignore current functions and create new ones for cli to use, itll be cleaner that way
    while True:
    
        cli = CLI()

        # sample_use()
        #sim_test()
        swarm_optimisation()

        loadedSwarm = []
        skip = False
        usrInput = ""

        #use match for navigation
        if skip == False:
            usrInput = cli.get_user_choice()

        match usrInput:
            case "run optimisation":
                params = cli.get_optimisation_params()
                loadedSwarm = optimize(**params)

            case "run simulation":
                availableAgents = range(len(loadedSwarm[0].agents)) if loadedSwarm else 0
                if availableAgents != 0:
                    params = cli.get_simulation_params(availableAgents)
                else:
                    print("Loaded swarm contains no agents. Please load a valid swarm before running a simulation.")

            case "save":
                if loadedSwarm == []:
                    print("No swarm loaded. Please run an optimisation or load a swarm before saving.")
                else:

                    swarm_params = {
                        'iteration': loadedSwarm[1],
                        'range_min': loadedSwarm[0].limit_min,
                        'range_max': loadedSwarm[0].limit_max,
                        'dimension': len(loadedSwarm[0].agents[0].values),
                        'number_of_agents': len(loadedSwarm[0].agents)
                    }
                    save_params = cli.get_save_params(swarm_params)

                    if save_params[1]: #if user wants to save all params
                        save.save_swarm_state(loadedSwarm[0], loadedSwarm[1], save_params[0])
                    else:
                        loadedSwarm[0].agents = [loadedSwarm[0].get_best_agent()] #only save best agent
                        save.save_swarm_state(loadedSwarm[0], loadedSwarm[1], save_params[0])


            case "load":
                load_params = cli.get_load_params(save.get_all_loadable_swarms())
                # Implement loading logic here
                loadedSwarmInfo = save.load_swarm_state(load_params)

                loadedSwarm = [agent_swarm(no_of_agents=loadedSwarmInfo['number_of_agents']),loadedSwarmInfo['iteration']]
                loadedSwarm[0].limit_min = loadedSwarmInfo['range_min']
                loadedSwarm[0].limit_max = loadedSwarmInfo['range_max']
                
                for agent in loadedSwarm[0].agents:
                    agent.values = loadedSwarmInfo['agents'][agent.agent_id]['values']
                    agent.fitness = loadedSwarmInfo['agents'][agent.agent_id]['fitness']
                    agent.bestPosition = loadedSwarmInfo['agents'][agent.agent_id]['best_position']
                    agent.velocity = loadedSwarmInfo['agents'][agent.agent_id]['velocity']
                    agent.History = loadedSwarmInfo['agents'][agent.agent_id]['history']

            case "exit":
                print("Exiting program.")
                break
