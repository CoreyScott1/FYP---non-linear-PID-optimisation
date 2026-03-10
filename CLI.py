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
        run
        
        """
        pass
    
    def get_optimisation_params(self):
        pass
    
    def get_load_params(self):
        pass

    def get_save_params(self):
        pass

    def get_loaded_swarm_params(self):
        pass