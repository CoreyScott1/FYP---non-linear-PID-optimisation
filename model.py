import math
from scipy.special import gamma



class ControlBase():
    def __init__(self):

        self.physical_params = {
        "l" : 0.5,
        "m" : 0.2,
        "k" : [1.0],
        "kl" : [9.0],
        "kp" : [(-2.0, 1.0)],
        "damping" : 0.1
        }

        self.running_params = {
        "angle" : 0.0,
        "angular_velocity" : 0.0,
        "time_step" : 0.01,
        }

    def arm_force(self, angle, angular_velocity=0):
        l, m, k, kl, kp, damping = map(self.physical_params.get, ("l", "m", "k", "kl", "kp", "damping"))
        
        torque = 0.0

        for spring in range(len(kp)):
            x = l * math.cos(angle)
            y = l * math.sin(angle)

            dx = x - kp[spring][0]
            dy = y - kp[spring][1]

            dist = math.sqrt(dx**2 + dy**2)
            stretch = dist - kl[spring]

            force_mag = k[spring] * stretch

            torque += force_mag * l * math.sin(angle)

        torque -= m * 9.81 * l * math.sin(angle)
        torque -= damping * angular_velocity

        return torque

    def sim_step(self, torque):

        dt = self.running_params["time_step"]
        l = self.physical_params["l"]
        m = self.physical_params["m"]

        I = m * l**2

        alpha = torque / I

        self.running_params["angular_velocity"] += alpha * dt
        self.running_params["angle"] += self.running_params["angular_velocity"] * dt

        return self.running_params["angular_velocity"], self.running_params["angle"]
    

class PIDController(ControlBase):
    def __init__(self, setpoint):
        super().__init__()

        self.Kp = 0.0
        self.Ki = 0.0
        self.Kd = 0.0

        self.lam = 1.0   
        self.mu = 1.0   

        self.setpoint = setpoint

        self.error_history = []
        self.integral = 0.0
        self.filtered_der = 0.0
        self.current_PID = 0.0

        self.max_mem = 2000
        self.u_min = -100.0
        self.u_max = 100.0
        self.alpha = 0.2

        self.int_coeffs = None
        self.der_coeffs = None

        self.prev_error = 0.0

    def fractional_coeffs(self, order, N):
        coeffs = [1.0]
        for k in range(1, N):
            coeff = coeffs[-1] * ((order - k + 1) / k)
            coeffs.append(coeff)
        return coeffs

    def reset(self):
        self.running_params["angle"] = 0.0
        self.running_params["angular_velocity"] = 0.0

        self.error_history = []
        self.integral = 0.0
        self.filtered_der = 0.0
        self.current_PID = 0.0
        self.prev_error = 0.0

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

        self.integral += error * dt
        self.integral = max(-100.0, min(100.0, self.integral))

        derivative = (error - self.prev_error) / dt
        self.prev_error = error

        self.filtered_der = (
            self.alpha * derivative +
            (1 - self.alpha) * self.filtered_der
        )

        u = (
            self.Kp * error +
            self.Ki * self.integral +
            self.Kd * self.filtered_der
        )

        u = max(self.u_min, min(self.u_max, u))

        self.current_PID = u
        return u
    

    def sim_run(self,time_limit):
        time_steps = int(time_limit / self.running_params["time_step"])
        velocity_history = []
        position_history = []
        set_points = []

        for step in range(time_steps):
            angle = self.running_params["angle"]
            velocity = self.running_params["angular_velocity"]

            control_torque = self.compute_control(angle)
            plant_torque = self.arm_force(angle, velocity)
            total_torque = control_torque + plant_torque


            v, p = self.sim_step(total_torque)

            velocity_history.append(v)
            position_history.append(p)
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
            return 1e7

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
    pid_controller = PIDController(setpoint=5)
    pid_controller.set_PID_params(P=5.0, I=1.5, D=2.0, lam=1, mu=1)

    velocity_history, position_history, set_points = pid_controller.sim_run(10.0)

    print("Final Position:", position_history[-1])

