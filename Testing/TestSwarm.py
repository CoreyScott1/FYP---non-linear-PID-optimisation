import unittest
from swarm import agent_swarm, PIDController

class TestAgent(unittest.TestCase):
    def setUp(self):
        from swarm import Agent
        self.agent = agent_swarm()


    def test_agent_initialization(self):
        self.agent = agent_swarm()

        self.assertEqual(self.agent.position, 0.0)
        self.assertEqual(self.agent.velocity, 0.0)
        self.assertEqual(self.agent.angle, 0.0)
    
    def test_agent_update(self):
        self.agent = agent_swarm()
        self.agent.position = 0.0
        self.agent.velocity = 0.0
        self.agent.update(force=10.0, time_step=0.1)
        expected_velocity = 1.0  # Assuming initial velocity is 0.0 and force is 10.0
        expected_position = 0.1  # Assuming initial position is 0.0 and velocity is 1.0
        self.assertEqual(self.agent.velocity, expected_velocity)
        self.assertEqual(self.agent.position, expected_position)

class TestSwarm(unittest.TestCase):
    def setUp(self):
        from swarm import agent_swarm
        self.swarm = agent_swarm(no_of_agents=5)

    def test_swarm_initialization(self):
        from swarm import agent_swarm
        swarm = agent_swarm(no_of_agents=5)
        self.assertEqual(len(swarm.agents), 5)
    
    def test_swarm_update_positions(self):
        from swarm import agent_swarm
        swarm = agent_swarm(no_of_agents=5)
        initial_positions = [agent.position for agent in swarm.agents]
        swarm.update_positions(time_step=0.1)
        updated_positions = [agent.position for agent in swarm.agents]
        self.assertNotEqual(initial_positions, updated_positions)



if __name__ == '__main__':
    unittest.main()