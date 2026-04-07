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



def plot_all_params(pointArray, x_ranges=None):
    num_plots = len(pointArray)
    
    # Create figure with subplots
    fig, axes = plt.subplots(num_plots, 1, figsize=(12, 2 * num_plots))
    
    # Handle single plot case (axes won't be an array)
    if num_plots == 1:
        axes = [axes]
    
    for i, point in enumerate(pointArray):
        x_range = x_ranges[i] if x_ranges and i < len(x_ranges) else None
        plot_number_line(point, x_range=x_range, ax=axes[i])
    
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
    """Animates a number line of an array of points with range"""

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
    

def plot_sector_convergence(swarm_or_histories, param_names=None):
    """
    Plot the convergence of each sector (parameter dimension) over iterations.
    
    Args:
        swarm_or_histories: Either a swarm object or list of agent histories
        param_names: Optional list of parameter names (default: ['P', 'I', 'D', 'Gamma', 'Mu'])
    """
    # Extract histories
    if hasattr(swarm_or_histories, 'agents'):
        # It's a swarm object
        histories = [agent.History for agent in swarm_or_histories.agents]
    else:
        # It's already a list of histories
        histories = swarm_or_histories
    
    if not histories or not histories[0]:
        print("No history data available")
        return
    
    # Set default parameter names
    if param_names is None:
        param_names = ['P', 'I', 'D', 'Gamma', 'Mu']
    
    num_params = len(histories[0][0][0])  # Number of parameters
    num_iterations = len(histories[0])     # Number of iterations
    
    # Extract best values and fitness for each iteration
    best_fitness_per_iteration = []
    best_params_per_iteration = [[] for _ in range(num_params)]
    avg_params_per_iteration = [[] for _ in range(num_params)]
    
    for iteration in range(num_iterations):
        best_fitness = float('inf')
        best_params = None
        
        # Collect all parameter values and fitness for this iteration
        all_params = [[] for _ in range(num_params)]
        
        for agent_history in histories:
            if iteration < len(agent_history):
                params, fitness = agent_history[iteration]
                
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_params = params
                
                for param_idx in range(num_params):
                    all_params[param_idx].append(params[param_idx])
        
        best_fitness_per_iteration.append(best_fitness)
        
        for param_idx in range(num_params):
            best_params_per_iteration[param_idx].append(best_params[param_idx])
            avg_params_per_iteration[param_idx].append(np.mean(all_params[param_idx]))
    
    # Create figure with subplots
    fig, axes = plt.subplots(num_params + 1, 1, figsize=(12, 3 * (num_params + 1)))
    
    iterations = np.arange(1, num_iterations + 1)
    
    # Plot fitness convergence (top subplot)
    axes[0].plot(iterations, best_fitness_per_iteration, 'b-', linewidth=2, label='Best Fitness')
    axes[0].set_xlabel('Iteration')
    axes[0].set_ylabel('Fitness (Error)')
    axes[0].set_title('Best Fitness Convergence')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    
    # Plot each parameter's convergence
    for param_idx, param_name in enumerate(param_names[:num_params]):
        ax = axes[param_idx + 1]
        ax.plot(iterations, best_params_per_iteration[param_idx], 'b-', linewidth=2, 
                label='Best Value', marker='o', markersize=4)
        ax.plot(iterations, avg_params_per_iteration[param_idx], 'r--', linewidth=1.5, 
                label='Average Value', marker='s', markersize=3, alpha=0.7)
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Parameter Value')
        ax.set_title(f'Sector {param_idx + 1}: Parameter {param_name} Convergence')
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    #test data
    param_array = [
        [10.0, 10.0, 8.0, 0.4, 0.7],
        [12.0, 8.0, 6.0, 0.5, 0.6],
        [8.0, 12.0, 10.0, 0.3, 0.8]
    ]

    for x in enumerate(param_array):
        print(f"Parameter Set {x[0]+1}: {x[1]}")   

    plot_all_params(param_array)




