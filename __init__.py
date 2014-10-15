"""**Librarian** is a small python library that provides two key features to
help both developers and python users alike:

* For **developers**, it provides a series of classes designed to help progress logging as well as in the control of I/O processes.

* For **users**, it provides a system to build a project's pipeline by tracking multiple python executions.

.. moduleauthor:: Jaume Bonet <jaume.bonet@gmail.com>

"""

from .metaclass     import *
from .abstractclass import *
from .main          import *
from .filesystem    import *


__all__ = []
__all__.extend(metaclass.__all__)
__all__.extend(abstractclass.__all__)
__all__.extend(main.__all__)
__all__.extend(filesystem.__all__)
