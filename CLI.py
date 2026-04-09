

class CLI():
    def __init__(self):
        pass

    def loose_match_prompt(self, options, response=None):

        candidate_options = []
    
        if response is None:
            response = list(input().lower().replace(" ", ""))
        print(f"Response: {response}")
        for option in options:
            indexList = []
            for letter in response:
                if letter in option:
                    indexList.append(option.index(letter))
            if list(option)[0] == response[0]: 
                if indexList == sorted(indexList):
            
                    candidate_options.append((option, len(indexList)))
        if candidate_options:
            return max(candidate_options, key=lambda x: x[1])[0] if candidate_options else None
        
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





    def get_user_choice(self): #used for default cmd when not in menu

        return self.loose_match_prompt(["save", "load", "run optimisation", "run simulation", "exit"])
    
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
        responses = cli.collection_prompt(collection_meassages, ["type", "type", "loose_match"], collection_constraints)
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


    def get_loaded_swarm_params(self):
        """
        select speficic iterations and elements of a swarm
        for inbetween get_load and get_simulation, called by main
        also can be used to navigate swarm stats, might break into seperate function
        """
        pass

if __name__ == "__main__":
    cli = CLI()
    loose_match_options = ["save", "load", "run optimisation", "run simulation", "exit"]
    while True:
        print("Please select an option:")
        print(cli.loose_match_prompt(loose_match_options))
