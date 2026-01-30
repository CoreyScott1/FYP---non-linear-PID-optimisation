import random
from simulation import evaluate_pid
import numpy as np


class agent:
    def __init__(self, dimension, range_min, range_max):
        self.values = []
        self.bestPosition = [[0.0 for _ in range(dimension)], float('inf')]
        self.fitness = [float('inf')]
        self.velocity = [0.0 for _ in range(dimension)]
        self.History = []

        for i in range(dimension):
            self.values.append(float(random.uniform(range_min, range_max)))
    
    def update_best_position(self):
        if self.bestPosition is None:
            self.bestPosition = [self.values.copy(), self.fitness]

        else:
            if self.fitness < self.bestPosition[1]:
                self.bestPosition = [self.values.copy(), self.fitness]
            else:
                pass
    
    def update_history(self):
        self.History.append((self.values, self.fitness))

class agent_swarm:
    def __init__(self, no_of_agents, dimension=3, range_min=0, range_max=100):
        self.agents = [agent(dimension, range_min, range_max) for _ in range(no_of_agents)]
        self.best_agent = self.agents[random.randint(0, no_of_agents -1)]
        self.intertia_weight =  0.768244
        self.cognitive_weight = 1.020288
        self.social_weight = 1.826533


    def update_fitness(self):
        for agent in self.agents:
            agent.fitness = evaluate_pid(agent.values[0], agent.values[1], agent.values[2])
            agent.update_best_position()
            agent.update_history()
        
    def get_best_agent(self):
        best_agent = min(self.agents, key=lambda agent: agent.fitness)
        self.best_agent = best_agent
        return best_agent

    def get_swarm_values(self):
        swarm_values = []
        for ag in self.agents:
            swarm_values.append(ag.values + [ag.fitness])
        return swarm_values


    def calculate_velocity(self):
        self.update_fitness()
        global_best_agent = self.get_best_agent()

        for agent in self.agents:

            #Main velocity equation

            intertia_component = self.intertia_weight * np.array(agent.velocity)  
            cognitive_component = self.cognitive_weight * random.random() * (np.array(agent.bestPosition[0])- np.array(agent.values))
            social_component = self.social_weight * random.random() * (np.array(global_best_agent.values) - np.array(agent.values))
            agent.velocity = intertia_component + cognitive_component + social_component


    def update_positions(self, time_step= 0.233868):
        self.calculate_velocity()
        for ag in self.agents:

            #Main position update equation
            values = list(np.array(ag.values) + np.array(ag.velocity) * time_step)
            for i in range(len(values)):
                if values[i] < 0:
                    values[i] = random.uniform(0, ag.values[i]) # random clamping
            ag.values = values
            
    def get_agent_histories(self):
        histories = []
        for ag in self.agents:
            histories.append(ag.History)
        return histories
    
    
if __name__ == "__main__":
    iterations = 10
    test_swarm = agent_swarm(50)
    run = []

    for i in range(iterations):

        test_swarm.update_positions()
        print(f"Iteration {i+1}: Best agent values: {test_swarm.best_agent.values}, fitness: {test_swarm.best_agent.fitness}")
        run.append(test_swarm.get_swarm_values())
    

    
    

    

