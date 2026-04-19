import unittest
from swarm import agent_swarm

class TestAgent(unittest.TestCase):
    def setUp(self):
        self.swarm = agent_swarm(no_of_agents=1)
        self.agent = self.swarm.agents[0]

    def test_agent_initialization(self):
        # Check dimensions
        self.assertEqual(len(self.agent.values), 5)
        self.assertEqual(len(self.agent.velocity), 5)

        # Check defaults
        self.assertEqual(self.agent.fitness, [float('inf')])
        self.assertEqual(len(self.agent.History), 0)

    def test_agent_best_position_update(self):
        # Simulate fitness update
        self.agent.fitness = 10
        self.agent.update_best_position()

        self.assertEqual(self.agent.bestPosition[1], 10)

        # Improve fitness
        self.agent.fitness = 5
        self.agent.update_best_position()

        self.assertEqual(self.agent.bestPosition[1], 5)


class TestSwarm(unittest.TestCase):
    def setUp(self):
        self.swarm = agent_swarm(no_of_agents=5)

    def test_swarm_initialization(self):
        self.assertEqual(len(self.swarm.agents), 5)

    def test_swarm_update_positions(self):
        initial_values = [ag.values.copy() for ag in self.swarm.agents]

        self.swarm.update_positions()

        updated_values = [ag.values for ag in self.swarm.agents]

        self.assertNotEqual(initial_values, updated_values)

    def test_swarm_best_agent(self):
        self.swarm.update_positions()
        best = self.swarm.get_best_agent()

        self.assertIsNotNone(best)
        self.assertTrue(hasattr(best, "fitness"))


if __name__ == '__main__':
    unittest.main()