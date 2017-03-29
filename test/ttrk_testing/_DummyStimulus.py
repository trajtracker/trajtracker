

class DummyStimulus(object):

    def __init__(self):
        self.presented = False
        self.position = (0, 0)

    def present(self, update=True, clear=True):
        self.presented = True
        self.presented_args = {'update': update, 'clear': clear}

