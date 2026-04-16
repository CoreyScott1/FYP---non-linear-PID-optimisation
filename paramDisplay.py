import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

 # Restructure from agents -> frames -> (parameters, fitness) to frames -> parameters -> agent values

def plot_velocity_position_history(velocity_history, position_history, time_limit):
    time_array = np.linspace(0, time_limit, len(velocity_history))
    
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(time_array, velocity_history)
    plt.xlabel('Time (s)')
    plt.ylabel('Angular Velocity (rad/s)')
    plt.title('Velocity History')
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(time_array, position_history)
    plt.xlabel('Time (s)')
    plt.ylabel('Angle (rad)')
    plt.title('Position History')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()






def plot_number_line(points, x_range=None, ax=None):
    """Plots a mumber line of an array of points with range"""
    points = np.array(points)
    
    # Determine x-axis range
    if x_range is None:
        x_min, x_max = points.min(), points.max()
        padding = (x_max - x_min) * 0.1 if x_max > x_min else 0.5
        x_range = (x_min - padding, x_max + padding)
    
    
    # Draw number line
    ax.plot(x_range, [0, 0], 'k-', linewidth=2)
    
    # Plot points
    ax.plot(points, [0] * len(points), 'ro', markersize=10)
    
    # Configure axes
    ax.set_xlim(x_range)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel('Value')
    ax.grid(axis='x', alpha=0.3)
    ax.set_yticks([])
    
    plt.tight_layout()
    plt.grid(True)

def animate_number_line(points_history, x_range=None, interval=100):

    if not points_history or not points_history[0]:
        return
    
    num_params = len(points_history[0])
    num_frames = len(points_history)
    
    # Create subplots for each parameter
    fig, axes = plt.subplots(num_params, 1, figsize=(12, 2 * num_params))
    if num_params == 1:
        axes = [axes]
    
    # Determine x-axis ranges for each parameter
    if x_range is None:
        x_ranges = []
        for param_idx in range(num_params):
            all_values = np.concatenate([frame[param_idx] for frame in points_history])
            x_min, x_max = all_values.min(), all_values.max()
            padding = (x_max - x_min) * 0.1 if x_max > x_min else 0.5
            x_ranges.append((x_min - padding, x_max + padding))
    else:
        x_ranges = x_range
    
    # Initialize lines and text for each parameter
    lines = []
    time_texts = []
    for param_idx, ax in enumerate(axes):
        ax.plot(x_ranges[param_idx], [0, 0], 'k-', linewidth=2)
        line, = ax.plot([], [], 'ro', markersize=10)
        time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
        ax.set_xlim(x_ranges[param_idx])
        ax.set_ylim(-0.5, 0.5)
        ax.set_xlabel('Value')
        ax.set_ylabel(f'Parameter {param_idx + 1}')
        ax.grid(axis='x', alpha=0.3)
        ax.set_yticks([])
        lines.append(line)
        time_texts.append(time_text)
    
    def init():
        for line in lines:
            line.set_data([], [])
        for time_text in time_texts:
            time_text.set_text('')
        return lines + time_texts
    
    def animate(frame):
        for param_idx in range(num_params):
            current_points = np.array(points_history[frame][param_idx])
            lines[param_idx].set_data(current_points, [0] * len(current_points))
            time_texts[param_idx].set_text(f'Frame: {frame}')
        return lines + time_texts
    
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=num_frames,
                                   interval=interval, blit=True, repeat=True)
    plt.tight_layout()
    plt.show()


def create_animation(physical_params, running_params, xPos, yPos, set_points_x, set_points_y):
    """
    Create animation of arm,
    reqires setpoint of arm
    """
    # Create animation
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Set up the plot limits
    max_range = physical_params["l"] + 1
    ax.set_xlim(-max_range, max_range)
    ax.set_ylim(-max_range, max_range)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_xlabel('X Position (m)')
    ax.set_ylabel('Y Position (m)')
    ax.set_title('Arm Animation')
    

    # Initialize line and point for the arm
    line, = ax.plot([], [], 'b-', lw=2)
    point, = ax.plot([], [], 'ro', markersize=8)
    setpoint, = ax.plot([], [], 'g*', markersize=15)
    spring_lines = [ax.plot([], [], 'g-', lw=1)[0] for _ in physical_params["kp"]]
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
    
    def init():
        line.set_data([], [])
        point.set_data([], [])
        setpoint.set_data([], [])
        for spring_line in spring_lines:
            spring_line.set_data([], [])
        time_text.set_text('')
        return [line, point, setpoint, time_text] + spring_lines
    
    def animate(frame):

        # Draw line from origin to arm endpoint
        line.set_data([0, xPos[frame]], [0, yPos[frame]])

        # Draw point at arm endpoint
        point.set_data([xPos[frame]], [yPos[frame]])

        # Draw setpoint
        setpoint.set_data([set_points_x[frame]], [set_points_y[frame]])

        # Draw spring lines from spring positions to arm endpoint
        for i, spring_line in enumerate(spring_lines):
            spring_pos = physical_params["kp"][i]
            spring_line.set_data([spring_pos[0], xPos[frame]], [spring_pos[1], yPos[frame]])
        
        # Update time text
        time_text.set_text(f'Time: {frame * running_params["time_step"]:.2f}s')
        return [line, point, setpoint, time_text] + spring_lines
    
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(xPos), 
                                   interval=running_params["time_step"] * 1000, blit=True, repeat=True)
    plt.show()
    
def plot_points_vs_time(x_points, time_limit=10):
    """Plot x points against time (0 to time_limit seconds)"""
    time_array = np.linspace(0, time_limit, len(x_points))
    
    plt.figure(figsize=(10, 6))
    plt.plot(time_array, x_points, 'b-', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('X Position (m)')
    plt.title('X Position vs Time')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

