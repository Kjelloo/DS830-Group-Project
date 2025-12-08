from Event import Event, EventType


class EventManager:
    def __init__(self):
        self.events = list[Event]

    def add_event(self, event: Event):
        self.events.append(event)

    def get_events(self):
        return self.events

    def get_event_by_type(self, status: EventType):
        return [event for event in self.events if event.event_type == status]