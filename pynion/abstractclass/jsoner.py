'''
@file: JSONer.py

@author: Jaume Bonet
@mail:   jaume.bonet@gmail.com
@date:   04/2014

@ [oliva's lab](http://sbi.imim.es)

@class: JSONer
'''
from abc import ABCMeta
import json

import jsonpickle

try:
    from .numpy_handlers import NPReadable
    from .numpy_handlers import register_numpy_handlers
    np_readable = NPReadable()
    register_numpy_handlers()
except:
    np_readable = None


class JSONer(object):
    __metaclass__ = ABCMeta

    def to_json(self, unpicklable = True, readable = False, api = False):
        if np_readable is not None:
            np_readable.status = readable
            np_readable.api    = api
        return jsonpickle.encode(self, unpicklable=unpicklable)

    def to_dict(self, unpicklable = True, readable = False, api = False):
        return json.loads(self.to_json(unpicklable, readable, api))

    @staticmethod
    def from_json(json_data):
        return jsonpickle.decode(json_data)
