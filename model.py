import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np



class ControlBase():
    def __init__(self):

        self.physical_params = {
        "l" : 5.0,  # length of the arm
        "m" : 2.0,  # mass of the arm
        "k" : [5.0], # spring constants
        "kl" : [2.0], #spring lengths
        "kp" : [(-7, 0)], # spring positions
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
        new_angle = self.running_params["angle"] + (current_velocity * time_step) % (2*math.pi)
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
        self.gamma = 0
        self.mu = 0
        self.setpoint = setpoint
        self.previous_error = [0]
        self.current_PID = 0
    
    def set_PID_params(self, P, I, D, gamma, mu):
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.gamma = gamma
        self.mu = mu

    def compute_control(self, current_angle): #implement FOPID
        error = self.setpoint - current_angle
        self.previous_error.append(error)

        P = self.Kp * error

        I = self.Ki * sum(self.previous_error) * self.running_params["time_step"]
        if I > 0:
            I = I ** self.gamma
        else:
            I = -(-I) ** self.gamma

        D = self.Kd * (error - self.previous_error[-2]) / self.running_params["time_step"]
        if D > 0:
            D = D ** self.mu
        else:
            D = -(-D) ** self.mu

        self.current_PID = P + I + D
        

        return self.current_PID
    

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
    
    def evaluate_performance(self, position_history):
        error_sum = 0
        for position in position_history:
            error_sum += abs(self.setpoint - position)
        return error_sum
    
    def complete_test(self, time_limit, P, I, D, gamma, mu):
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.gamma = gamma
        self.mu = mu
        velocity_history, position_history, _ = self.sim_run(time_limit)
        performance = self.evaluate_performance(position_history)
        return performance


if __name__ == "__main__":
    # Example usage
    pid_controller = PIDController(Kp=10.0, Ki=10.0, Kd=8.0, gamma=0.4, mu=0.7, setpoint=2*math.pi/3)
    velocity_history, position_history, set_points = pid_controller.sim_run(10.0)
    print("Final Position:", position_history[-1])
    