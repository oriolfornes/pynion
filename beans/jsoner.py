'''
@file: JSONer.py

@author: Jaume Bonet
@mail:   jaume.bonet@gmail.com
@date:   04/2014

@ [oliva's lab](http://sbi.imim.es)

@class: JSONer
'''
import json
from abc import ABCMeta, abstractmethod


class JSONer(object):
    '''
    Children from this class have the toJSON() method to be exported in json
    format.
    Every children must implement the _toDICT() method that will be used to
    format every attribute in a way that is json-compatible.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def _toDICT(self):
        '''
        Mandatory method to implement in children of the {JSONer} class.
        Describes the class as a dictionary with all the values compatible with
        the json format.

        @return: {Dictionary}
        '''
        raise NotImplementedError()

    def toJSON(self, pretty=False):
        '''
        Transforms the data of the class into a json formated String.
        Requires as_dict() function to be implemented.

        @param:    pretty
        @pdef:     Whether or not to prettify the json.
        @pdefault: _False_
        @ptype:    {Boolean}

        @return: {String}
        '''
        if pretty:
            return json.dumps(self._toDICT(), indent=2, separators=(',', ':'))
        return json.dumps(self._toDICT(), separators=(',', ':'))
