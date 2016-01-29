# -*-
#
# @author: jaumebonet
# @email:  jaume.bonet@gmail.com
# @url:    jaumebonet.github.io
#
# @date:   2016-01-29 17:03:51
#
# @last modified by:   jaumebonet
# @last modified time: 2016-01-29 17:51:38
#
# -*-


class RepeatedExtendedAttributeException(Exception):
    pass


class ProtectedExtendedAttributeException(Exception):
    pass


class UndeclaredProtectedAttributeException(Exception):
    pass


def extendable(original_class):
    """The **extendable** class decorators provides the methods to allow the
    controlled addition and retrieval of attributes to the class.

    The recipie for overwritting the __init__ method is adapted from
    http://stackoverflow.com/a/682242/2806632
    """
    orig_init = original_class.__init__     # copy original __init__

    def _check_W_attribute(self, attribute):
        if self._ext[attribute] is None: return True
        if attribute not in self._ext_protected: return True
        return False

    def _check_D_attribute(self, attribute, force):
        if force: return True
        if attribute not in self._ext_protected: return True
        return False

    def declare_attribute(self, attribute, protected = False):
        if attribute not in self._ext:
            self._ext[attribute] = None
            if protected:
                self._ext_protected.add(attribute)
        else:
            raise RepeatedExtendedAttributeException

    def set_attribute(self, attribute, value):
        if attribute in self._ext:
            if self._check_W_attribute(attribute):
                self._ext[attribute] = value
            else:
                raise ProtectedExtendedAttributeException
        else:
            raise UndeclaredProtectedAttributeException

    def get_attribute(self, attribute):
        if attribute in self._ext:
            return self._ext[attribute]
        else:
            raise UndeclaredProtectedAttributeException

    def del_attribute(self, attribute, force = False):
        if attribute in self._ext:
            if self._check_D_attribute(attribute, force):
                del(self._ext[attribute])
                self._ext_protected.discard(attribute)
            else:
                raise ProtectedExtendedAttributeException
        else:
            raise UndeclaredProtectedAttributeException

    def __init__(self, *args, **kws):       # new __init__
        orig_init(self, *args, **kws)       # call the original __init__
        self._ext = {}
        self._ext_protected = set()

    original_class.__init__ = __init__      # set new __init__
    original_class._check_W_attribute  = _check_W_attribute
    original_class._check_D_attribute  = _check_D_attribute
    original_class.declare_attribute   = declare_attribute
    original_class.set_attribute       = set_attribute
    original_class.get_attribute       = get_attribute
    original_class.del_attribute       = del_attribute

    return original_class
