
from trajtracker.misc.nvshapes import Rectangle


class DummyStimulus(Rectangle):

    def __init__(self, position=(0, 0), size=(100, 100)):
        super(DummyStimulus, self).__init__(size, position)
        self.presented = False
        self.presented_args = {}

    def present(self, update=True, clear=True):
        self.presented = True
        self.presented_args = {'update': update, 'clear': clear}

