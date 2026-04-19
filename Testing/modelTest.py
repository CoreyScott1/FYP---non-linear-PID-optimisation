import unittest
from model import ControlBase, PIDController


class TestControlBase(unittest.TestCase):
    def setUp(self):
        self.model = ControlBase()

    def test_arm_force_zero_angle(self):
        force = self.model.arm_force(angle=0.0, angular_velocity=0.0)

        # At angle = 0, sin(0)=0 so torque should be ~0 (no gravity or spring torque)
        self.assertAlmostEqual(force, 0.0, places=5)

    def test_sim_step(self):
        self.model.running_params["angular_velocity"] = 0.0
        self.model.running_params["angle"] = 0.0
        self.model.running_params["time_step"] = 0.1

        velocity, angle = self.model.sim_step(torque=10.0)

        self.assertNotEqual(velocity, 0.0)
        self.assertNotEqual(angle, 0.0)


class TestPIDController(unittest.TestCase):
    def setUp(self):
        self.pid = PIDController(setpoint=1.0)
        self.pid.set_PID_params(P=2.0, I=0.5, D=1.0, lam=1.0, mu=1.0)

    def test_compute_control_positive_error(self):
        u = self.pid.compute_control(current_angle=0.0)
        self.assertGreater(u, 0.0)

    def test_compute_control_negative_error(self):
        u = self.pid.compute_control(current_angle=2.0)
        self.assertLess(u, 0.0)

    def test_compute_control_zero_error(self):
        u = self.pid.compute_control(current_angle=1.0)
        self.assertAlmostEqual(u, 0.0, places=5)

    def test_sim_run_lengths(self):
        self.pid.running_params["time_step"] = 0.1
        v_hist, p_hist, sp = self.pid.sim_run(time_limit=1.0)

        self.assertEqual(len(v_hist), 10)
        self.assertEqual(len(p_hist), 10)
        self.assertEqual(len(sp), 10)

    def test_complete_test(self):
        fitness = self.pid.complete_test(
            time_limit=1.0,
            P=2.0, I=0.5, D=1.0,
            lam=1.0, mu=1.0,
            setpoint=1.0
        )

        self.assertIsInstance(fitness, float)
        self.assertGreaterEqual(fitness, 0.0)


class TestFitnessEvaluation(unittest.TestCase):
    def setUp(self):
        self.pid = PIDController(setpoint=1.0)
        self.pid.set_PID_params(P=2.0, I=0.5, D=1.0, lam=1.0, mu=1.0)

    def test_evaluate_performance_valid(self):
        v_hist, p_hist, _ = self.pid.sim_run(time_limit=1.0)
        fitness = self.pid.evaluate_performance(p_hist, v_hist, 1.0)

        self.assertIsInstance(fitness, float)

    def test_evaluate_performance_nan(self):
        fitness = self.pid.evaluate_performance(
            position_history=[float("nan")],
            velocity_history=[0.0],
            setpoint=1.0
        )

        self.assertEqual(fitness, 1e9)


if __name__ == '__main__':
    unittest.main()