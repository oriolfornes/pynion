"""

@author: Jaume Bonet
@mail:   jaume.bonet@gmail.com
@date:   2014

@ [oliva's lab](http://sbi.imim.es)

"""
from .. import errors


def multiton(cls):
    try:
        identifier = cls._IDENTIFIER
    except AttributeError:
        identifier = 'name'

    class M(cls):
        instances = {}

        def __new__(c, *args, **kwargs):
            if kwargs and identifier in kwargs:
                classid = kwargs[identifier]
            else:
                if len(args) > 0:
                    classid = args[0]
                else:
                    raise errors.DecoratorErrorBadMultitonIdentifier([identifier,
                                                                      cls.__name__])
            if cls not in c.instances:
                c.instances.setdefault(cls, {})
            if classid not in c.instances[cls]:
                c.instances[cls][classid] = cls.__new__(c, *args, **kwargs)
            return c.instances[cls][classid]
    M.__name__ = cls.__name__
    return M
