class EventDispatcher:
    def __init__(self):
        self.listeners = {}

    def register(self, event_type, callback):
        self.listeners.setdefault(event_type, []).append(callback)

    def dispatch(self, event):
        for callback in self.listeners.get(event.event_type, []):
            callback(event)
