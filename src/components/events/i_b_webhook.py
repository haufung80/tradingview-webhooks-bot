from components.events.base.event import Event


class IBWebhook(Event):
    def __init__(self):
        super().__init__()
