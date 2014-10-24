"""Metaclasses in **pynion** are designed in order to help users develop
their classes by adding a certain build behavior to the derived classes.

.. moduleauthor:: Jaume Bonet <jaume.bonet@gmail.com>

"""

__all__ = ["Singleton", "Multiton"]

from .tones import Singleton
from .tones import Multiton
