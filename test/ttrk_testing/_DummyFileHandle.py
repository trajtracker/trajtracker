

class DummyFileHandle(object):

    def __init__(self):
        self._data = ""


    def write(self, data):
        self._data += data


    def close(self):
        pass

    @property
    def data(self):
        return self._data
