from components.actions.base.action import Action
from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 4001, clientId=0)

class IBOrderExecute(Action):
    def __init__(self):
        super().__init__()

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # this is required
        """
        Custom run method. Add your custom logic here.
        """
        print(self.name, '---> action has run!')
        print(ib.positions())

