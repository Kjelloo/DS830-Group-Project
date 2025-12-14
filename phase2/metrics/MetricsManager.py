import os

import matplotlib.pyplot as plt
import dearpygui.dearpygui as dpg

from phase2.metrics.Event import EventType
from phase2.metrics.EventManager import EventManager


class MetricsManager:
    """
    Manages metrics and generates plots based on events recorded during a simulation run.

    A run is identified by a string `run_id`. During a run, events are saved to a CSV
    under `phase2/metrics/runs/<run_id>/<run_id>.csv`. This manager reads those events
    and can produce different plots to help you analyze the simulation.

    Plots available:
    - Requests over time: delivered, expired, and pending counts.
    - Driver mutations: how many times each driver changed behaviour.
    - Behaviour deliveries: cumulative deliveries grouped by driver behaviour.
    """

    def __init__(self, run_id: str):
        """
        Create a MetricsManager bound to a specific run.

        Args:
            run_id (str): Unique identifier for the simulation run whose events should be analyzed.

        Side effects:
        - Initializes an EventManager to read events from the run's CSV file.
        - Preloads event lists for convenience.
        """
        self.run_id = run_id
        self.event_manager = EventManager(self.run_id)
        self.all_events = self.event_manager.get_events()
        self.req_expired = self.event_manager.get_events_by_type(EventType.REQUEST_EXPIRED)
        self.req_delivered = self.event_manager.get_events_by_type(EventType.REQUEST_DELIVERED)

    def _get_run_output_dir(self) -> str:
        """
        Return the output directory for this run and create it if missing.

        Returns:
            The absolute path to `phase2/metrics/runs/<run_id>/` where plot images can be saved.
        """
        base_dir = os.path.abspath(os.path.dirname(__file__))
        runs_dir = os.path.join(base_dir, "runs")
        run_dir = os.path.join(runs_dir, self.run_id)
        if not os.path.exists(run_dir):
            os.makedirs(run_dir, exist_ok=True)
        return run_dir

    def _plot_requests_over_time(self, save: bool = False):
        """
        Plot delivered, expired, and pending request counts over time.

        This plot is built by scanning the event stream in chronological order and
        maintaining counters for each request status. At each event timestamp, we record
        a snapshot of the totals to draw three lines: Delivered, Expired, and Pending.

        Args:
            save (bool): If True, save the figure as `<run_id>_requests_over_time.png` inside the
                  run's output folder. If False, only show the plot.
        """
        if not self.all_events:
            print("No events recorded. Skipping Requests Over Time plot.")
            return

        # Sort events by timestamp to process chronologically
        events = sorted(self.all_events, key=lambda e: e.timestamp)

        total_generated = 0
        total_delivered = 0
        total_expired = 0

        times = []
        delivered_series = []
        expired_series = []
        pending_series = []

        # Process events, update counters and capture snapshot at each event time
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

        plt.figure(figsize=(10, 6))
        plt.plot(times, delivered_series, label="Delivered", color="g")
        plt.plot(times, expired_series, label="Expired", color="r")
        plt.plot(times, pending_series, label="Pending", color="b")
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

    def _plot_driver_mutations(self, save: bool = False):
        """
        Plot how many times each driver mutated (changed behaviour).

        We count `BEHAVIOUR_CHANGED` events per driver and draw a simple bar chart
        showing mutation counts. This is useful to see which drivers changed their
        behaviour the most during the run.

        Args:
            save (bool): If True, save the figure as `<run_id>_driver_mutations.png` inside the
                  run's output folder. If False, show the plot interactively.
        """
        # Count mutations per driver from events
        events = self.event_manager.get_events_by_type(EventType.BEHAVIOUR_CHANGED)
        if not events:
            print("No BEHAVIOUR_CHANGED events recorded; skipping Driver Mutations plot.")
            return

        counts = {}
        for ev in events:
            if ev.driver_id is None:
                continue
            if ev.driver_id not in counts:
                counts[ev.driver_id] = 0
            counts[ev.driver_id] += 1

        if not counts:
            print("No driver IDs found in BEHAVIOUR_CHANGED events. Skipping Driver Mutations plot.")
            return

        driver_ids = sorted(counts.keys())
        mutation_counts = [counts[d] for d in driver_ids]

        # Plot bar chart
        plt.figure(figsize=(10, 6))
        plt.bar([str(d) for d in driver_ids], mutation_counts, color="c")
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
        """Plot cumulative deliveries grouped by driver behaviour over time.

        For each delivery event, we look up the driver's behaviour active at that
        timestamp by scanning that driver's behaviour change events (which include the
        behaviour name). We then increment the cumulative count for that behaviour and
        record a snapshot. The result is a set of lines that grow over time, one per
        behaviour (EarningsMaxBehaviour, GreedyDistanceBehaviour, LazyBehaviour).

        Args:
            save: If True, save the figure as `<run_id>_behaviour_deliveries.png` inside the
                  run's output folder. If False, show the plot interactively.
        """
        # Get all deliveries and behaviour change events
        deliveries = self.event_manager.get_events_by_type(EventType.REQUEST_DELIVERED)
        behaviour_changes = self.event_manager.get_events_by_type(EventType.BEHAVIOUR_CHANGED)

        # If no deliveries at all, there's nothing to plot
        if not deliveries:
            print("No deliveries recorded. Skipping Behaviour Deliveries plot.")
            return

        # Build a simple timeline (sorted list) of behaviour changes per driver
        # Example: {driver_id: [Event(... at t=0), Event(... at t=50), ...], ...}
        changes_by_driver = {}
        for ev in behaviour_changes:
            if ev.driver_id is None:
                continue
            if ev.driver_id not in changes_by_driver:
                changes_by_driver[ev.driver_id] = []
            changes_by_driver[ev.driver_id].append(ev)
        # Sort each driver's changes by time so we can scan from earliest to latest
        for driver_id in changes_by_driver:
            changes_by_driver[driver_id].sort(key=lambda e: e.timestamp)

        # Helper: given a driver and a time, return the behaviour name the driver had
        # Look for the latest change at or before the given time
        def _get_behaviour_name(driver_id: int, at_time: int) -> str:
            changes = changes_by_driver.get(driver_id, [])
            last_name = None
            for change in changes:
                if change.timestamp <= at_time:
                    last_name = change.behaviour_name
                else:
                    # once we pass the time, stop scanning
                    break
            if last_name is None:
                return "Unknown"
            return last_name

        # Prepare cumulative counts per behaviour over time
        deliveries_sorted = sorted(deliveries, key=lambda e: e.timestamp)
        times = []
        behaviour_counts_over_time = {
            "EarningsMaxBehaviour": [],
            "GreedyDistanceBehaviour": [],
            "LazyBehaviour": []
        }
        cumulative_counts = {
            "EarningsMaxBehaviour": 0,
            "GreedyDistanceBehaviour": 0,
            "LazyBehaviour": 0
        }

        # Process each delivery event in chronological order
        for ev in deliveries_sorted:
            driver_id = ev.driver_id if ev.driver_id is not None else -1
            name = _get_behaviour_name(driver_id, ev.timestamp)

            # If behaviour name is not one of the known keys, treat as Unknown
            if name not in cumulative_counts:
                name = "Unknown"

            cumulative_counts[name] += 1
            times.append(ev.timestamp)

            # Record snapshot for each behaviour
            for key in behaviour_counts_over_time:
                behaviour_counts_over_time[key].append(cumulative_counts[key])

        # Plot lines. We only draw a line if it has non-zero values to keep the plot clean.
        plt.figure(figsize=(10, 6))
        if any(v > 0 for v in behaviour_counts_over_time["EarningsMaxBehaviour"]):
            plt.plot(times, behaviour_counts_over_time["EarningsMaxBehaviour"], label="EarningsMaxBehaviour")
        if any(v > 0 for v in behaviour_counts_over_time["GreedyDistanceBehaviour"]):
            plt.plot(times, behaviour_counts_over_time["GreedyDistanceBehaviour"], label="GreedyDistanceBehaviour")
        if any(v > 0 for v in behaviour_counts_over_time["LazyBehaviour"]):
            plt.plot(times, behaviour_counts_over_time["LazyBehaviour"], label="LazyBehaviour")

        plt.xlabel("Ticks")
        plt.ylabel("Cumulative Deliveries")
        plt.title(f"Deliveries by Behaviour Over Time (Run {self.run_id})")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.4)
        plt.tight_layout()

        # Save the figure to the run folder if requested, otherwise show it
        if save:
            out_dir = self._get_run_output_dir()
            out_path = os.path.join(out_dir, f"{self.run_id}_behaviour_deliveries.png")
            plt.savefig(out_path)
            plt.show()
        else:
            plt.show()

    def generate_plots(self, save: bool = False):
        """
        Generate all available plots for this run.

        Convenience method that calls each plotting function in turn. Use `save=True`
        to write images into the run's output folder.

        Args:
            save (bool): If True, save all plots into the run's output folder. If False,
                  show the plots interactively.
        """
        self._plot_requests_over_time(save=save)
        self._plot_driver_mutations(save=save)
        self._plot_behaviour_deliveries(save=save)