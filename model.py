import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
from scipy.special import gamma
import time



class ControlBase():
    def __init__(self):

        self.physical_params = {
        "l" : 30.0,  # length of the arm
        "m" : 20.0,  # mass of the arm
        "k" : [1.0], # spring constants
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
    def __init__(self, setpoint):
        super().__init__()
        self.Kp = 0
        self.Ki = 0
        self.Kd = 0
        self.lam = 1.0 
        self.mu = 1.0

        self.setpoint = setpoint

        self.error_history = []
        self.current_PID = 0
        self.filtered_der = 0.0

        self.max_mem = 40
        self.u_min = -100.0
        self.u_max = 100.0
        self.alpha = 0.2  # derivative smoothing

        # Coefficients cache
        self.int_coeffs = None
        self.der_coeffs = None
    
    def fractional_coeffs(self, order, N):
            coeffs = [1.0]
            for k in range(1, N):
                coeffs.append(coeffs[-1] * (1 - (order + 1) / k))
            return coeffs
    
    def reset(self):
        self.running_params["angle"] = 0.0
        self.running_params["angular_velocity"] = 0.0
        self.previous_error = [0]
        self.current_PID = 0

        self.error_history = []
        self.current_PID = 0
        self.filtered_der = 0.0
    
    def set_PID_params(self, P, I, D, lam, mu, setpoint=None):
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.lam = lam
        self.mu = mu
        
        if setpoint is not None:
            self.setpoint = setpoint
        
        self.int_coeffs = self.fractional_coeffs(self.lam, self.max_mem)
        self.der_coeffs = self.fractional_coeffs(self.mu, self.max_mem)

    def compute_control(self, current_angle):
        dt = self.running_params["time_step"]

        error = self.setpoint - current_angle

        self.error_history.insert(0, error)
        if len(self.error_history) > self.max_mem:
            self.error_history.pop()

        e_hist = self.error_history
        n = len(e_hist)


        if self.int_coeffs is None or self.der_coeffs is None:
            self.int_coeffs = self.fractional_coeffs(self.lam, self.max_mem)
            self.der_coeffs = self.fractional_coeffs(self.mu, self.max_mem)


        frac_int = sum(
            self.int_coeffs[i] * e_hist[i]
            for i in range(n)
        ) * (dt ** self.lam)

        raw_der = sum(
            self.der_coeffs[i] * e_hist[i]
            for i in range(n)
        ) / (dt ** self.mu)

        self.filtered_der = (
            self.alpha * raw_der +
            (1 - self.alpha) * self.filtered_der
        )

        frac_der = self.filtered_der

        u = (
            self.Kp * error +
            self.Ki * frac_int +
            self.Kd * frac_der
        )

        #u = max(self.u_min, min(self.u_max, u))

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
        pos = position_history
        vel = velocity_history
        dt = self.running_params["time_step"]

        
        if any(p != p or abs(p) == float('inf') for p in pos):
            return 1e9

        max_pos = max(abs(p) for p in pos)
        if max_pos > 2 * abs(setpoint) + 1e-6:
            return 1e7  # unstable / runaway


        error = [setpoint - p for p in pos]


        iae = sum(abs(e) for e in error) * dt

        overshoot = max(0.0, max(p - setpoint for p in pos))
        overshoot_penalty = overshoot**2


        sign_changes = sum(
            1 for i in range(1, len(error))
            if error[i] * error[i - 1] < 0
        )

        oscillation_penalty = sign_changes**2

        vel_energy = sum(v*v for v in vel) / (len(vel) + 1e-6)


        if hasattr(self, "control_history") and len(self.control_history) > 1:
            u = self.control_history
            control_effort = sum(abs(u[i] - u[i-1]) for i in range(1, len(u)))
        else:
            control_effort = 0.0


        final_error = abs(error[-1])
        settling_penalty = final_error * 10.0


        fitness = (
            1.0 * iae +
            2.0 * overshoot_penalty +
            3.0 * oscillation_penalty +
            2.0 * vel_energy +
            settling_penalty
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
    pid_controller = PIDController(setpoint=math.pi)
    pid_controller.set_PID_params(P=2.0, I=0.5, D=1.0, lam=1, mu=1)
    velocity_history, position_history, set_points = pid_controller.sim_run(10.0)
    print("Final Position:", position_history[-1])

