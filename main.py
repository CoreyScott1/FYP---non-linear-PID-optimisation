from model import PIDController 
from swarm import agent_swarm
from paramDisplay import *
from CLI import CLI
import numpy as np
import math
import save


def animation_init(simulation_params):

    pid_controller = PIDController(simulation_params['setpoint'])
    pid_controller.set_PID_params(simulation_params['P'], simulation_params['I'], simulation_params['D'], simulation_params['gamma'], simulation_params['mu'], simulation_params['setpoint'])
    velocity_history, position_history, set_points = pid_controller.sim_run(time_limit=10.0, control_enabled=True)

    xPos = [pid_controller.physical_params["l"] * math.cos(angle) for angle in position_history]
    yPos = [pid_controller.physical_params["l"] * math.sin(angle) for angle in position_history]
    set_points_x = [pid_controller.physical_params["l"] * math.cos(angle) for angle in set_points]
    set_points_y = [pid_controller.physical_params["l"] * math.sin(angle) for angle in set_points]

    # Create and display animation
    create_animation(pid_controller.physical_params, pid_controller.running_params, xPos, yPos, set_points_x, set_points_y)

    plot_points_vs_time(velocity_history)


def optimize(params):
    setpoint = 4
    swarm = agent_swarm(no_of_agents=params[0])
    iterations = params[1]
    if params[2] == "yes":
        show_animation = True
    else:
        show_animation = False

    pid_controller = PIDController(setpoint)

    for i in range(iterations):
        print(f"Iteration {i+1}/{iterations}")
        swarm.update_positions(iteration=i)
        print(f"Best Agent Fitness: {swarm.get_best_agent().fitness}")
        print(f"Best Agent Parameters: {swarm.get_best_agent().values}")
    if show_animation:

        simulation_params = {
            'P': swarm.get_best_agent().values[0],
            'I': swarm.get_best_agent().values[1],
            'D': swarm.get_best_agent().values[2],
            'gamma': swarm.get_best_agent().values[3],
            'mu': swarm.get_best_agent().values[4],
            'setpoint': setpoint
        }
        animation_init(simulation_params)

        agent_history = swarm.get_agent_histories()
    
        # Restructure from agents -> frames -> (parameters, fitness) to frames -> parameters -> agent values
        num_frames = len(agent_history[0]) if agent_history else 0
        num_params = len(agent_history[0][0][0]) if agent_history and agent_history[0] else 0
        formatted_histories = [
            [[agent[frame_idx][0][param_idx] for agent in agent_history] for param_idx in range(num_params)]
            for frame_idx in range(num_frames)
        ]
        ranges = [(0, 50), (0, 50), (0, 50), (0, 1), (0, 1)]

        animate_number_line(formatted_histories, x_range=ranges, interval=500)
    
    print("Optimization Complete!")
    best_agent = swarm.get_best_agent()

    print(f"Best Agent Fitness: {best_agent.fitness}")
    print(f"Best Agent Parameters: {best_agent.values}")

    print("Returning to main menu...")
    return(swarm, i)


def CLI_loop():
    #ignore current functions and create new ones for cli to use, itll be cleaner that way
    cli = CLI()
    
    run = True
    loadedSwarm = []
    
    while run == True:

        skip = False
        usrInput = ""

        #use match for navigation
        if skip == False:
            usrInput = cli.get_user_choice()

        match usrInput:
            case "run optimisation":
                params = cli.get_optimisation_params()
                loadedSwarm = optimize(params)

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
                if loadedSwarmInfo['iteration'] is None:
                    iteration = 0
                else:
                    iteration = loadedSwarmInfo['iteration']
                loadedSwarm = [agent_swarm(no_of_agents=loadedSwarmInfo['number_of_agents']), iteration]
                loadedSwarm[0].limit_min = loadedSwarmInfo['range_min']
                loadedSwarm[0].limit_max = loadedSwarmInfo['range_max']
                
                for i, agent in enumerate(loadedSwarm[0].agents):
                    agent.values = loadedSwarmInfo['agents'][i]['values']
                    agent.fitness = loadedSwarmInfo['agents'][i]['fitness']
                    agent.bestPosition = loadedSwarmInfo['agents'][i]['best_position']
                    agent.velocity = loadedSwarmInfo['agents'][i]['velocity']
                    agent.History = loadedSwarmInfo['agents'][i]['history']
                skip = True
                usrInput = "animation nav" #skip straight to animation nav after loading a swarm
            
            case "animate":
                print("Animating best agent from loaded swarm...")

                simulation_params = {
                'P': loadedSwarm[0].get_best_agent().values[0],
                'I': loadedSwarm[0].get_best_agent().values[1],
                'D': loadedSwarm[0].get_best_agent().values[2],
                'gamma': loadedSwarm[0].get_best_agent().values[3],
                'mu': loadedSwarm[0].get_best_agent().values[4],
                'setpoint': setpoint
                }
                
                animation_init(simulation_params)

                agent_history = swarm.get_agent_histories()
            
                # Restructure from agents -> frames -> (parameters, fitness) to frames -> parameters -> agent values
                num_frames = len(agent_history[0]) if agent_history else 0
                num_params = len(agent_history[0][0][0]) if agent_history and agent_history[0] else 0
                formatted_histories = [
                    [[agent[frame_idx][0][param_idx] for agent in agent_history] for param_idx in range(num_params)]
                    for frame_idx in range(num_frames)
                ]
                ranges = [(0, 50), (0, 50), (0, 50), (0, 1), (0, 1)]

                animate_number_line(formatted_histories, x_range=ranges, interval=500)


                        



if __name__ == "__main__":
    bestagents = []
    setpoint = 4
    for x in save.get_all_loadable_swarms():
    
        loadedSwarmInfo = save.load_swarm_state(x)
        if loadedSwarmInfo['iteration'] is None:
            iteration = 0
        else:
            iteration = loadedSwarmInfo['iteration']
        loadedSwarm = [agent_swarm(no_of_agents=loadedSwarmInfo['number_of_agents']), iteration]
        loadedSwarm[0].limit_min = loadedSwarmInfo['range_min']
        loadedSwarm[0].limit_max = loadedSwarmInfo['range_max']
        
        for i, agent in enumerate(loadedSwarm[0].agents):
            agent.values = loadedSwarmInfo['agents'][i]['values']
            agent.fitness = loadedSwarmInfo['agents'][i]['fitness']
            agent.bestPosition = loadedSwarmInfo['agents'][i]['best_position']
            agent.velocity = loadedSwarmInfo['agents'][i]['velocity']
            agent.History = loadedSwarmInfo['agents'][i]['history']
        
        
        bestagents.append(loadedSwarm[0].get_best_agent())
    print("Best Agents from all loaded swarms:")
    for agent in bestagents:

        simulation_params = {
                'P': agent.values[0],
                'I': agent.values[1],
                'D': agent.values[2],
                'gamma': agent.values[3],
                'mu': agent.values[4],
                'setpoint': setpoint 
            }
        print(agent.fitness)


        #animation_init(simulation_params)
        


        

