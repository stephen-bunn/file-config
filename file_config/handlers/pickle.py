# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

from ._common import BaseHandler


class PickleHandler(BaseHandler):
    """ The Pickle serialization handler.
    """

    name = "pickle"
    packages = ("pickle",)
    options = {}

    def on_pickle_dumps(self, pickle, dictionary):
        """ The :mod:`pickle` dumps method.
        """

        return pickle.dumps(dictionary, protocol=pickle.HIGHEST_PROTOCOL)

    def on_pickle_loads(self, pickle, content):
        """ The :mod:`pickle` loads method.
        """

        return pickle.loads(content)
