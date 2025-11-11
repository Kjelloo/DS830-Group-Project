from datetime import datetime
import os
import matplotlib.pyplot as plt

folder = "statistics"
os.makedirs(folder, exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
file_name = f"stats_{timestamp}.csv"

filepath = os.path.join(folder, file_name)

def record_step_to_file(state, metrics, filename=filepath) -> None:
    """
    Record a single simulation step to a text file.

    Args:
        state (dict): Current state of the simulation.
        metrics (dict): Metrics for the current step.
        filename (str): File to append the data to.
    """
    served = metrics["served"]
    expired = metrics["expired"]
    queued = len(state["pending"])
    time_step = state["t"]

    # Append data to file (create if it doesn't exist)
    try:
        with open(filename, 'a') as f:
            f.write(f"{time_step},{served},{expired},{queued}\n")
    except Exception as e:
        print(f"Could not write to file: {e}")


def start_new_simulation_log(filename=filepath) -> None:
    """
    Start a new simulation by creating/clearing the data file with headers.
    Args:
        filename (str): File to create.
    """
    try:
        with open(filename, 'w') as f:
            f.write("time_step,served_cumulative,expired_cumulative,queued_current\n")
    except Exception as e:
        print(f"Could not create log file: {e}")


def _read_simulation_data(filename=filepath) -> tuple[list[int], list[int], list[int], list[int]]:
    """
    Read simulation data from file and return lists of data.
    Args:
        filename (str): File to read data from.
    """
    time_steps = []
    served = []
    expired = []
    queued = []

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()[1:]  # Skip header line

            for line in lines:
                line = line.strip()
                if line:  # Skip empty lines
                    parts = line.split(',')
                    if len(parts) == 4:
                        time_steps.append(int(parts[0]))
                        served.append(int(parts[1]))
                        expired.append(int(parts[2]))
                        queued.append(int(parts[3]))
    except Exception as e:
        print(f"Could not read data file: {e}")
        return [], [], [], []

    return time_steps, served, expired, queued


def create_requests_plot(filename=filepath, save_plot=False) -> None:
    """
    Create and display a plot of served, expired, and queued requests over time.

    Args:
        filename (str): File to read data from.
        save_plot (bool): Whether to save the plot as a PNG file.
    """
    # Read data from file
    time_steps, served, expired, queued = _read_simulation_data(filename)

    # Check if data is available
    if not time_steps:
        print("No data found to plot")
        return

    # Create the plot
    plt.figure(figsize=(12, 8))

    plt.plot(time_steps, served, label='Served (Cumulative)', color='green', linewidth=2)
    plt.plot(time_steps, expired, label='Expired (Cumulative)', color='red', linewidth=2)
    plt.plot(time_steps, queued, label='Queued (Current)', color='blue', linewidth=2)

    plt.xlabel('Time Steps', fontsize=12)
    plt.ylabel('Number of Requests', fontsize=12)
    plt.title('Simulation results: Request Status Over Time', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save the plot if requested
    if save_plot:
        plot_filename = f"statistics/plot_{timestamp}.png"
        try:
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {plot_filename}")
        except Exception as e:
            print(f"Could not save plot: {e}")

    plt.show()


def print_summary_stats(filename=filepath) -> None:
    """
    Print summary statistics from the simulation data.
    Args:
        filename (str): File to read data from.
    """
    time_steps, served, expired, queued = _read_simulation_data(filename)

    if not time_steps:
        print("No data found")
        return

    final_served = served[-1] if served else 0
    final_expired = expired[-1] if expired else 0
    final_queued = queued[-1] if queued else 0
    max_queue = max(queued) if queued else 0
    avg_queue = sum(queued) / len(queued) if queued else 0
    total_steps = len(time_steps)

    print("\nSimulation Summary:")
    print(f"Total Steps: {total_steps}")
    print(f"Requests Served: {final_served}")
    print(f"Requests Expired: {final_expired}")
    print(f"Requests Queued: {final_queued}")
    print(f"Max Queue Length: {max_queue}")
    print(f"Avg Queue Length: {avg_queue:.2f}")
    print(f"Total Requests: {final_served + final_expired + final_queued}")


# Simple convenience function to generate everything after simulation
def generate_report(filename=filepath) -> None:
    """
    Generate complete report with stats and plot.
    Args:
        filename (str): File to read data from.
    """
    print_summary_stats(filename)
    create_requests_plot(filename, True)
