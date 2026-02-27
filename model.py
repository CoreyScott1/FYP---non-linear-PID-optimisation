import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import random
from scipy.special import gamma



class ControlBase():
    def __init__(self):

        self.physical_params = {
        "l" : 30.0,  # length of the arm
        "m" : 20.0,  # mass of the arm
        "k" : [5.0], # spring constants
        "kl" : [9.0], #spring lengths
        "kp" : [(-37, 10)], # spring positions
        "damping" : 0.9 # damping coefficient
        }


        self.running_params = {
        "angle" : 0.0,
        "angular_velocity" : 0.0,
        "time_step" : 0.01,
        }


    def arm_force(self, angle, angular_velocity=0):
        l, m, k, kl, kp, damping = map(self.physical_params.get, ("l", "m", "k", "kl", "kp", "damping"))
        force = 0

        for spring in range(len(kp)):
            sum_distance = math.sqrt(
            ((((l)*(math.cos(angle)))-kp[spring][0]))**2 +
            (((l)*(math.sin(angle))-kp[spring][1]))**2 
            ) - kl[spring]

            f_spring = k[spring] * sum_distance

            force += f_spring * math.sin(angle) / l

        #gravity component
        f_gravity = m * 9.81 * math.cos(angle) / l
        force -= f_gravity
        
        # damping component
        f_damping = damping * angular_velocity
        force -= f_damping
        
        return force

    def velocity_update(self, force, time_step):
        new_velocity = self.running_params["angular_velocity"] + (force * time_step)
        self.running_params["angular_velocity"] = new_velocity
        return new_velocity

    def angle_update(self, current_velocity, time_step: float):
        new_angle = (self.running_params["angle"] + (current_velocity * time_step)) % (2*math.pi)
        self.running_params["angle"] = new_angle
        return new_angle
    
    def sim_step(self, force):

        new_velocity = self.velocity_update(force, self.running_params["time_step"])
        new_angle = self.angle_update(new_velocity, self.running_params["time_step"])

        velocity = new_velocity
        position= new_angle

        return velocity, position
    
class PIDController(ControlBase):
    def __init__(self, setpoint=2*math.pi/3):
        super().__init__()
        self.Kp = 0
        self.Ki = 0
        self.Kd = 0
        self.lam = 0
        self.mu = 0
        self.setpoint = setpoint
        self.previous_error = [0]
        self.current_PID = 0
    
    def reset(self):
        self.running_params["angle"] = 0.0
        self.running_params["angular_velocity"] = 0.0
        self.previous_error = [0]
        self.current_PID = 0
    
    def set_PID_params(self, P, I, D, lam, mu, setpoint=None):
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.lam = lam
        self.mu = mu
        if setpoint is not None:
            self.setpoint = setpoint

    def compute_control(self, current_angle):  # implement FOPID
        Kp, Ki, Kd, lam, mu = map(self.__dict__.get, ("Kp", "Ki", "Kd", "lam", "mu"))
        dt = self.running_params["time_step"]
        
        error = self.setpoint - current_angle
        self.previous_error.append(error)
        N = len(self.previous_error)

        # --- Helper function: safe fractional coefficients ---
        def fractional_coeffs(alpha, N):
            coeffs = [1.0]
            for k in range(1, N):
                coeffs.append(coeffs[k-1] * (alpha - k + 1) / k)
            return coeffs

        # Fractional Integral
        int_coeffs = fractional_coeffs(lam, N)
        frac_int = sum(c * e for c, e in zip(int_coeffs[::-1], self.previous_error)) * dt**lam

        # Fractional Derivative
        der_coeffs = fractional_coeffs(mu, N)
        frac_der = sum(c * e for c, e in zip(der_coeffs[::-1], self.previous_error)) / dt**mu

        # Compute control force
        u = Kp * error + Ki * frac_int + Kd * frac_der
        self.current_PID = u
        return u
    

    def sim_run(self,time_limit, control_enabled=True):
        time_steps = int(time_limit / self.running_params["time_step"])
        velocity_history = []
        position_history = []
        set_points = []

        for step in range(time_steps):
            current_angle = self.running_params["angle"]
            current_velocity = self.running_params["angular_velocity"]
            if control_enabled:
                control_force = self.compute_control(current_angle) + super().arm_force(current_angle, current_velocity)
            else:
                control_force = super().arm_force(current_angle, current_velocity)
            velocity, position = self.sim_step(force=control_force)
            velocity_history.append(velocity)
            position_history.append(position)
            set_points.append(self.setpoint)

        return velocity_history, position_history, set_points
    
    
    def evaluate_performance(self, position_history, velocity_history, setpoint):
        pos = np.array(position_history)
        vel = np.array(velocity_history)
        dt = self.running_params["time_step"]
        T = len(pos) * dt

        error = setpoint - pos
        iae = np.sum(np.abs(error)) * dt

        overshoot = np.max(pos - setpoint)
        overshoot_penalty = max(0.0, overshoot)**2

        tol = 0.02 * abs(setpoint) if abs(setpoint) > 1e-6 else 0.02
        settled_idx = None
        for i in range(len(pos)):
            if np.all(np.abs(error[i:]) < tol):
                settled_idx = i
                break

        if settled_idx is None:
            settling_penalty = T * 5.0  # never settled → big penalty
        else:
            settling_time = settled_idx * dt
            settling_penalty = settling_time

        vel_rms = np.sqrt(np.mean(vel**2))
        oscillation_penalty = vel_rms


        if np.any(np.isnan(pos)) or np.any(np.isinf(pos)):
            return 1e9  # instant death to unstable solutions

        if np.max(np.abs(pos)) > 10 * abs(setpoint + 1e-6):
            return 1e8  # diverged

        fitness = (
        1.0 * iae +
        5.0 * overshoot_penalty +
        3.0 * settling_penalty +
        2.0 * oscillation_penalty
        )

        return fitness
    
    def complete_test(self, time_limit, P, I, D, lam, mu, setpoint):
        self.reset()
        self.set_PID_params(P=P, I=I, D=D, lam=lam, mu=mu, setpoint=setpoint)
        

        velocity_history, position_history, set_points = self.sim_run(time_limit)
        performance = self.evaluate_performance(position_history, velocity_history, set_points[0])
        return performance


if __name__ == "__main__":
    # Example usage
    pid_controller = PIDController(setpoint=2*math.pi/3)
    pid_controller.set_PID_params(P=2.0, I=0.5, D=1.0, lam=1, mu=1)
    velocity_history, position_history, set_points = pid_controller.sim_run(10.0)
    print("Final Position:", position_history[-1])

    # for angle in np.linspace(0, 2*math.pi, 100):
    #     print(f"Angle: {angle:.2f}, Control Signal: {pid_controller.compute_control(current_angle=angle):.2f}")
