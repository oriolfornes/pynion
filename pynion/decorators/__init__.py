# -*-
#
# @author: jaumebonet
# @email:  jaume.bonet@gmail.com
# @url:    jaumebonet.github.io
#
# @date:   2016-01-29 17:03:38
#
# @last modified by:   jaumebonet
# @last modified time: 2016-02-16 19:25:12
#
# -*-
"""Decorators in **pynion** are designed in order to provide extra functionality
   to selected classes and functions.

.. moduleauthor:: Jaume Bonet <jaume.bonet@gmail.com>

"""
from .extendable import extendable
from .accepts    import accepts

__all__ = ["extendable", "accepts"]
