# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# MIT License <https://opensource.org/licenses/MIT>

from ._common import BaseHandler


class PickleHandler(BaseHandler):

    name = "pickle"
    packages = ("pickle",)

    def on_pickle_dumps(self, pickle, dictionary):
        return pickle.dumps(dictionary, protocol=pickle.HIGHEST_PROTOCOL)

    def on_pickle_loads(self, pickle, content):
        return pickle.loads(content)
