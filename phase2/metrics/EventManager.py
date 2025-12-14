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
                        "wait_time, "
                        "behaviour_name\n")

    def add_event(self, event: Event):
        # Append the event to csv file
        with open(self.filepath, 'a') as f:
            f.write("{timestamp}, "
                    "{event_type}, "
                    "{driver_id}, "
                    "{request_id}, "
                    "{wait_time}, "
                    "{behaviour_name}"
                    .format(timestamp=event.timestamp,
                            event_type=event.event_type.value,
                            driver_id=event.driver_id,
                            request_id=event.request_id,
                            wait_time=event.wait_time,
                            behaviour_name=event.behaviour_name if event.behaviour_name is not None else 'None') + '\n')

    def get_events(self):
        with open(self.filepath, 'r') as f:
            lines = f.readlines()
            # Skip header line if present
            data_lines = lines[1:] if lines and lines[0].startswith("timestamp") else lines

            events = []
            for line in data_lines:
                line = line.strip()
                if not line:
                    continue
                values = line.split(', ')
                # Require 6 fields (new format)
                if len(values) != 6:
                    continue
                ts, et, did, rid, wt, behaviour_name = values
                behaviour_name = None if behaviour_name == 'None' else behaviour_name
                try:
                    event = Event(timestamp=int(ts),
                                  event_type=EventType(int(et)),
                                  driver_id=int(did) if did != 'None' else None,
                                  request_id=int(rid) if rid != 'None' else None,
                                  wait_time=int(wt) if wt != 'None' else None,
                                  behaviour_name=behaviour_name)
                except ValueError:
                    continue
                events.append(event)
            return events

    def get_events_by_type(self, status: EventType):
        events = self.get_events()
        filtered_events = [event for event in events if event.event_type == status]
        return filtered_events
