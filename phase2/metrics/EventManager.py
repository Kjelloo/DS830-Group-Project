from __future__ import annotations

import os

from phase2.metrics.Event import Event, EventType


class EventManager:
    def __init__(self, run_id: str):
        # Place each run in its own subfolder: runs/<run_id>/<run_id>.csv
        base_dir = os.path.abspath(os.path.dirname(__file__))
        runs_dir = os.path.join(base_dir, "runs")
        run_dir = os.path.join(runs_dir, run_id)
        self.filepath = os.path.join(run_dir, f"{run_id}.csv")

        # Ensure directories exist
        if not os.path.exists(run_dir):
            os.makedirs(run_dir, exist_ok=True)

        # Initialize CSV file with header if it does not exist
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                f.write("timestamp, "
                        "event_type, "
                        "driver_id, "
                        "request_id, "
                        "wait_time\n")

    def add_event(self, event: Event):
        # Append the event to csv file
        with open(self.filepath, 'a') as f:
            f.write("{timestamp}, "
                    "{event_type}, "
                    "{driver_id}, "
                    "{request_id}, "
                    "{wait_time}"
                    .format(timestamp=event.timestamp,
                            event_type=event.event_type.value,
                            driver_id=event.driver_id,
                            request_id=event.request_id,
                            wait_time=event.wait_time) + '\n')

    def get_events(self):
        with open(self.filepath, 'r') as f:
            lines = f.readlines()[1:]  # Skip header line

            events = []
            for line in lines:
                line = line.strip()
                if line:  # Skip empty lines
                    values = line.split(', ')
                    if len(values) == 5:
                        try:
                            event = Event(timestamp=int(values[0]),
                                          event_type=EventType(int(values[1])),
                                          driver_id=int(values[2]) if values[2] != 'None' else None,
                                          request_id=int(values[3]) if values[3] != 'None' else None,
                                          wait_time=int(values[4]) if values[4] != 'None' else None)
                        except ValueError:
                            continue
                        events.append(event)
            return events

    def get_events_by_type(self, status: EventType):
        events = self.get_events()
        filtered_events = [event for event in events if event.event_type == status]
        return filtered_events
