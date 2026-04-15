

class CLI():
    def __init__(self):
        pass

    def loose_match_prompt(self, options, response=None):
        print(options)

        candidate_options = []
        try:
    
            if response == None:
                print("getting response")
                response = list(input().lower().replace(" ", ""))

            for option in options:
                indexList = []
                for letter in response:
                    if letter in option:
                        indexList.append(option.index(letter))
                if list(option)[0] == response[0]: 
                    if indexList == sorted(indexList):
                
                        candidate_options.append((option, len(indexList)))
            print(f"Candidate options: {candidate_options}")
            if len(candidate_options) > 0:
                return max(candidate_options, key=lambda x: x[1])[0] if candidate_options else None
            
            print("No valid options found, please try again.")
            return self.loose_match_prompt(options)
        
        except Exception as e:
            print("invalid input, please try again")
            return self.loose_match_prompt(options)

    def confirmation_prompt(self, message, default_yes=True):
        print(message)
        response = input().lower().strip()
        if response == "" and default_yes:
            return True
        else:
            loose_match_options = ["yes", "no"]
            return self.loose_match_prompt(loose_match_options, response) == "yes"
    
    def type_prompt(self, message, expected_type):
        print(message)
        while True:
            response = input().strip()
            try:
                return expected_type(response)
            except ValueError:
                print(f"Invalid input. Please enter a value of type {expected_type.__name__}.")
                return self.type_prompt(message, expected_type)
    
    def range_prompt(self, message, min_value=None, max_value=None):
        while True:
            try:
                value = float(input(message))
                if (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
                    print(f"Please enter a value between {min_value} and {max_value}.")
                else:
                    return value
            except ValueError:
                print("Invalid input. Please enter a numeric value.")
                return self.range_prompt(message, min_value, max_value)
    
    def collection_prompt(self, messages, response_types, constraints=None): 
        responses = []

        for i, message in enumerate(messages):

            if response_types[i] == "type":
                responses.append(self.type_prompt(message, constraints[i]))
            elif response_types[i] == "range":
                responses.append(self.range_prompt(message, constraints[i][0], constraints[i][1]))
            else:
                responses.append(self.loose_match_prompt(constraints[i], self.type_prompt(message, str)))
        return responses
    
    def int_range_prompt(self, message, min_value=None, max_value=None):
        while True:
            try:
                value = int(input(message))
                if (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
                    print(f"Please enter an integer between {min_value} and {max_value}.")
                else:
                    return value
            except ValueError:
                print("Invalid input. Please enter an integer value.")
                return self.int_range_prompt(message, min_value, max_value)





    def get_user_choice(self): #used for default cmd when not in menu
        print("Please select an option: \n Save\n Load\n Run optimization\n Run simulation\n Animation Nav\n Exit")
        response = self.loose_match_prompt(["save", "load", "run optimisation", "run simulation", "animation nav", "exit"])
        return response
    
    def get_optimisation_params(self):

        collection_meassages = [
            "Enter the number of agents: ",
            "Enter the number of iterations: ",
            "Show animation during optimization? (yes/no): "
        ]
        collection_constraints = [
            int,
            int,
            ["yes", "no"]
        ]
        responses = self.collection_prompt(collection_meassages, ["type", "type", "loose_match"], collection_constraints)
        return responses
        

    def get_simulation_params(self, agent_range):

        collection_meassages = [
            "Enter the setpoint: ",
            "Enter the time duration: ",
            "Select an agent to simulate: "
        ]
        collection_constraints = [
            float,
            float,
            agent_range 
        ]
        responses = cli.collection_prompt(collection_meassages, ["type", "type", "loose_match"], collection_constraints)
        return responses
    
    def get_load_params(self, available_swarms):

        print("Available saved swarms:")
        for i, swarm in enumerate(available_swarms):
            print(f"{i + 1}. {swarm}")
        return self.loose_match_prompt(available_swarms, self.type_prompt("Enter the name of the swarm to load: ", str))
    

    def get_save_params(self, swarm_params):

        for key, value in swarm_params.items():
            print(f"{key}: {value}")
        
        all_params = self.confirmation_prompt("Do you want to save all agent history or just the final state? (yes for all, no for final state only): ")
        name = self.type_prompt("Enter a name for the saved swarm: ", str)
        return name, all_params


    def animation_nav(self,  loadedSwarmInfo):
        """
        select speficic iterations and elements of a swarm
        for inbetween get_load and get_simulation, called by main
        also can be used to navigate swarm stats, might break into seperate function
        """
        nav = True
        while nav == True:
            print("Loaded swarm:")
            for key, value in loadedSwarmInfo.items():
                print(f"{key}: {value}")
            print("Select an option: \n Iteration Navigation\n Select Agent\n Exit")
            response = self.loose_match_prompt(["iteration navigation", "select agent", "exit"])
            print(f"Response: {response}")
            match response:
                case "iteration navigation":
                    try:

                        if len(loadedSwarmInfo['agentData'][0]['history']) == 0:
                            print("No history data available for this swarm.")
                            continue

                        print(f"Iteration count: {len(loadedSwarmInfo['agentData'][0]['history'])}")

                        if self.confirmation_prompt("Do you want to view a specific iteration? (yes/no): "):
                            iteration = self.int_range_prompt("Enter the iteration number to view: ", 0, len(loadedSwarmInfo['agentData'][0]['history']) - 1)

                            print(f"Viewing iteration {iteration}...")
                            
                            iteration_data = [agent['history'][iteration] for agent in loadedSwarmInfo['agentData']]

                            for agent in iteration_data:
                                print(f"Agent values: {agent['values']}, fitness: {agent['fitness']}")
                            
                            response = self.loose_match_prompt(["yes", "no"], self.type_prompt("View another iteration? (yes/no) or  ", str))
                        
                        else:
                            print("Starting at iteration 0, enter < to go back an iteration, > to go forward an iteration, or exit to stop navigation.")
                            iteration = 0
                            while True:
                                print(f"Viewing iteration {iteration}...")
                                iteration_data = [agent['history'][iteration] for agent in loadedSwarmInfo['agentData']]

                                for agent in iteration_data:
                                    print(f"Agent values: {agent['values']}, fitness: {agent['fitness']}")
                                
                                nav_response = self.loose_match_prompt(["<", ">", "exit"], self.type_prompt("Enter <, >, or exit: ", str))
                                if nav_response == "<":
                                    iteration = max(0, iteration - 1)
                                elif nav_response == ">":
                                    iteration = min(len(loadedSwarmInfo['agentData'][0]['history']) - 1, iteration + 1)
                                else:
                                    break
                    except Exception as e:
                        print(f"Error retrieving iteration data: {e}")

                case "select agent":

                    try:

                        print(f"Number of agents: {len(loadedSwarmInfo['agentData'])}")
                        selected_agent = self.range_prompt("Enter the agent number to view: ", 1, len(loadedSwarmInfo['agentData'])) - 1
                        print(f"Viewing agent {selected_agent}...")
                        agent_data = loadedSwarmInfo['agentData'][selected_agent]
                        for i, iteration in enumerate(agent_data['history']):
                            print(f"Iteration {i}: Agent values: {iteration['values']}, fitness: {iteration['fitness']}")
                        
                        response = self.range_prompt("Select iteration to animate (enter -1 to skip): ", -1, len(agent_data['history']) - 1)
                        if response != -1:
                            print(f"Animating iteration {response} for agent {selected_agent}...")
                            iteration_data = agent_data['history'][response]
                            return ("run animation", iteration_data) #return data to animate in main
                    except Exception as e:
                        print(f"Error retrieving agent data: {e}")
                    
                case "exit":                    
                    return "back"

if __name__ == "__main__":
    cli = CLI()
    loose_match_options = ["save", "load", "run optimisation", "run simulation", "exit"]
    while True:
        print("Please select an option:")
        print(cli.loose_match_prompt(loose_match_options))
