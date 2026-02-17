from pyexpat import model
import unittest


class TestControlBase(unittest.TestCase):
    def setUp(self):
        from model import ControlBase
        self.model = ControlBase()

    def test_velocity_update(self):
        updated_velocity = self.model.velocity_update(force=10.0, time_step=0.1)
        expected_velocity = 1.0  # Assuming initial velocity is 0.0
        self.assertEqual(updated_velocity, expected_velocity)
    
    def test_angle_update(self):
        self.model.running_params["angle"] = 0.0  # Initial angle
        updated_angle = self.model.angle_update(current_velocity=1.0, time_step=0.1)
        expected_angle = 0.1  # Assuming initial angle is 0.0 and velocity is 1.0
        self.assertEqual(updated_angle, expected_angle)

    def test_arm_force(self):
        self.model.running_params["angular_velocity"] = 0.0
        self.model.running_params["angle"] = 0.0
        force = self.model.arm_force(angle=0.0, angular_velocity=0.0)
        expected_force = -3.9240000000000004  # Calculated based on the arm_force method with given parameters
        self.assertEqual(force, expected_force)
    
    def test_sim_step(self):
        self.model.running_params["angular_velocity"] = 0.0
        self.model.running_params["angle"] = 0.0
        self.model.running_params["time_step"] = 0.1
        velocity, position = self.model.sim_step(force=10.0)
        expected_velocity = 1.0  # Assuming initial velocity is 0.0 and force is 10.0
        expected_position = 0.1  # Assuming initial angle is 0.0 and velocity is 1.0
        self.assertEqual(velocity, expected_velocity)
        self.assertEqual(position, expected_position)

class TestPIDController(unittest.TestCase):
    def setUp(self):
        from model import PIDController
        self.pid = PIDController(setpoint=1.0)
        self.pid.set_PID_params(P=2.0, I=0.5, D=1.0, gamma=1.0, mu=1.0)

    def test_compute_control(self):
        control_signal = self.pid.compute_control(current_angle=0.5)
        expected_control_signal = 51.0025  # Calculated based on the compute_control method with given parameters
        self.assertEqual(control_signal, expected_control_signal)
    
    def test_compute_control_with_previous_error(self):
        self.pid.previous_error = [0.5, 0.25]  # Simulate previous errors
        control_signal = self.pid.compute_control(current_angle=0.5)
        expected_control_signal = 51.0025  # Calculated based on the compute_control method with given parameters and previous errors
        self.assertEqual(control_signal, expected_control_signal)
    
    def test_compute_control_with_negative_error(self):
        control_signal = self.pid.compute_control(current_angle=1.5)
        expected_control_signal = -51.0025  # Calculated based on the compute_control method with given parameters and negative error
        self.assertEqual(control_signal, expected_control_signal)
    
    def test_compute_control_with_zero_error(self):
        control_signal = self.pid.compute_control(current_angle=1.0)
        expected_control_signal = 0.0  # Calculated based on the compute_control method with given parameters and zero error
        self.assertEqual(control_signal, expected_control_signal)
    
    def test_sim_run(self):
        velocity_history, position_history, set_points = self.pid.sim_run(time_limit=1.0, control_enabled=True)
        self.assertEqual(len(velocity_history), 10)  # Assuming time_step is 0.1 and time_limit is 1.0
        self.assertEqual(len(position_history), 10)  # Assuming time_step is 0.1 and time_limit is 1.0
        self.assertEqual(len(set_points), 10)  # Assuming time_step is 0.1 and time_limit is 1.0
    
class TestFitnessEvaluation(unittest.TestCase):
    def setUp(self):
        from model import PIDController
        self.pid = PIDController(setpoint=1.0)
        self.pid.set_PID_params(P=2.0, I=0.5, D=1.0, gamma=1.0, mu=1.0)

    def test_evaluate_performance(self):
        performance = self.pid.evaluate_performance(time_limit=1.0)
        expected_performance = 10.0  # Assuming time_step is 0.1 and time_limit is 1.0
        self.assertEqual(performance, expected_performance)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestControlBase)
    #suite.addTest(TestPIDController)
    suite.addTest(TestFitnessEvaluation)
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())