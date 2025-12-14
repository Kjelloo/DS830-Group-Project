import matplotlib.pyplot as plt
import os
from collections import Counter
from phase2.metrics.Event import EventType
from phase2.metrics.EventManager import EventManager


class MetricsManager:
    """
    Manages metrics and generates plots based on events recorded during a simulation run.

    Args:
        run_id (str): The unique identifier for the simulation run.

    Plots to be generated include:
    - Number of completed, expired, and pending requests over time
    - Average wait time of requests over time
    - Each driver mutation amount over time
    - Which behaviour has had the most amount of deliveries over time
    """
    def __init__(self,  run_id: str):
        self.run_id = run_id
        self.event_manager = EventManager(self.run_id)
        self.all_events = self.event_manager.get_events()
        self.req_expired = self.event_manager.get_events_by_type(EventType.REQUEST_EXPIRED)
        self.req_delivered = self.event_manager.get_events_by_type(EventType.REQUEST_DELIVERED)

    def _get_run_output_dir(self) -> str:
        # Mirror EventManager path logic: runs/<run_id>/
        base_dir = os.path.abspath(os.path.dirname(__file__))
        runs_dir = os.path.join(base_dir, "runs")
        run_dir = os.path.join(runs_dir, self.run_id)
        if not os.path.exists(run_dir):
            os.makedirs(run_dir, exist_ok=True)
        return run_dir

    def _plot_requests_over_time(self, save: bool = False):
        # Aggregate counts over time based on event stream
        if not self.all_events:
            print("No events recorded; skipping Requests Over Time plot.")
            return

        # Sort events by timestamp to process chronologically
        events = sorted(self.all_events, key=lambda e: e.timestamp)

        # Counters
        total_generated = 0
        total_delivered = 0
        total_expired = 0

        # Series for plotting
        times = []
        delivered_series = []
        expired_series = []
        pending_series = []

        # Process events; update counters and capture snapshot at each event time
        for ev in events:
            if ev.event_type == EventType.REQUEST_GENERATED:
                total_generated += 1
            elif ev.event_type == EventType.REQUEST_DELIVERED:
                total_delivered += 1
            elif ev.event_type == EventType.REQUEST_EXPIRED:
                total_expired += 1

            pending = max(total_generated - total_delivered - total_expired, 0)

            times.append(ev.timestamp)
            delivered_series.append(total_delivered)
            expired_series.append(total_expired)
            pending_series.append(pending)

        # Plot
        plt.figure(figsize=(10, 6))
        plt.plot(times, delivered_series, label="Delivered", color="tab:green")
        plt.plot(times, expired_series, label="Expired", color="tab:red")
        plt.plot(times, pending_series, label="Pending", color="tab:blue")
        plt.xlabel("Ticks")
        plt.ylabel("Amount of Requests")
        plt.title(f"Requests Over Time (Run {self.run_id})")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.4)
        plt.tight_layout()

        if save:
            out_dir = self._get_run_output_dir()
            out_path = os.path.join(out_dir, f"{self.run_id}_requests_over_time.png")
            plt.savefig(out_path)
            plt.show()
        else:
            plt.show()

    def _plot_average_wait_time(self, save: bool = False):
        pass

    def _plot_driver_mutations(self, save: bool = False):
        # Count mutations per driver from events
        events = self.event_manager.get_events_by_type(EventType.BEHAVIOUR_CHANGED)
        if not events:
            print("No BEHAVIOUR_CHANGED events recorded; skipping Driver Mutations plot.")
            return

        # Tally by driver_id
        counts = Counter()
        for ev in events:
            # Only count if driver_id is present
            if ev.driver_id is not None:
                counts[ev.driver_id] += 1

        if not counts:
            print("No driver IDs found in BEHAVIOUR_CHANGED events; skipping Driver Mutations plot.")
            return

        # Prepare data for plotting
        driver_ids = sorted(counts.keys())
        mutation_counts = [counts[d] for d in driver_ids]

        # Plot bar chart
        plt.figure(figsize=(10, 6))
        plt.bar([str(d) for d in driver_ids], mutation_counts, color="tab:purple")
        plt.xlabel("Driver ID")
        plt.ylabel("Mutation Count")
        plt.title(f"Driver Behaviour Mutations (Run {self.run_id})")
        plt.grid(True, axis='y', linestyle='--', alpha=0.4)
        plt.tight_layout()

        if save:
            out_dir = self._get_run_output_dir()
            out_path = os.path.join(out_dir, f"{self.run_id}_driver_mutations.png")
            plt.savefig(out_path)
            plt.show()
        else:
            plt.show()

    def _plot_behaviour_deliveries(self, save: bool = False):
        pass

    def generate_plots(self, save: bool = False):
        self._plot_requests_over_time(save=save)
        self._plot_average_wait_time(save=save)
        self._plot_driver_mutations(save=save)
        self._plot_behaviour_deliveries(save=save)
        pass
