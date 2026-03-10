"""
logic controlled by main, CLI returns the values needed.
eg
run_optimisation(CLI.get_optimisation_params())


params to change
- number of agents
- number of iterations
- show animation during optimization (boolean)
- run for specific iteration count
- 

when in load section, show list of saved swarms and allow user to select one to load
can select specific iteration to show animation for, or just show final iteration

saving can save the current agent

"""


class CLI():
    def __init__(self):
        pass

    def get_user_choice(self): #used for default cmd when not in menu
        """
        save
        load
        run optimisation
        run simulation
        exit
        """
        pass
    
    def get_optimisation_params(self):
        """
        number of agents
        number of iterations
        show animation

        """
        pass

    def get_simulation_params(self):
        """
        setpoint
        time duration
        selected agent

        """
        pass
    
    def get_load_params(self):
        """
        show list of saved swarms
        select one to load
        - go back to main menu
        """
        pass

    def get_save_params(self):
        """
        show current swarm parameters
        select which parameters to save (or all)
        set name
        """
        pass

    def get_loaded_swarm_params(self):
        """
        select speficic iterations and elements of a swarm
        for inbetween get_load and get_simulation, called by main
        also can be used to navigate swarm stats, might break into seperate function
        """
        pass