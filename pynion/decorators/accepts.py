# -*-
#
# @author: jaumebonet
# @email:  jaume.bonet@gmail.com
# @url:    jaumebonet.github.io
#
# @date:   2016-02-16 18:40:22
#
# @last modified by:   jaumebonet
# @last modified time: 2016-02-16 19:34:44
#
# -*-
import json
from ..main.manager import Manager

m = Manager()


class ParameterTypeError(Exception):
    def __init__(self, pname, pexpected):
        self._pname = pname
        self._pexpt = pexpected

    def __str__(self):
        return 'arg {0._pname} does not match {0._pexpt}'.format(self)


def accepts(**types):
    """Allows to assert the type of the parameters of a function/method.

    One can specify, by name, only those parameters that expects to be checked.
    Special cases:
    * If the parameter is defined as "json" it will be checked for (str, dict)
    * If the parameter is defined as "json_dict" it will be checked for
    (str, dict) but it will ensure that it is passed to the function as dict
    * If the parameter is defined as "json_str" it will be checked for
    (str, dict) but it will ensure that it is passed to the function as string


    Usage as

    ::

        from pynion import accepts

        @accepts(int, (int,float))
            def func(arg1, arg2):
                return arg1 * arg2

    Adapted from http://code.activestate.com/recipes/578809-decorator-to-check-method-param-types/

    """
    def check_accepts(f):
        def new_f(*args, **kwds):
            for i, v in enumerate(args):
                kwds[f.func_code.co_varnames[i]] = v
            args = []
            for k, v in kwds.iteritems():
                if k not in types: continue
                if not isinstance(types[k], str) and not isinstance(v, types[k]):
                    raise ParameterTypeError(k, types[k])
                if isinstance(types[k], str):
                    tagname = types[k]
                    if tagname.startswith("json"):
                        if isinstance(v, (str, dict)):
                            if tagname == "json_dict":
                                if isinstance(v, str):
                                    kwds[k] = json.loads(v)
                            if tagname == "json_str":
                                if isinstance(v, dict):
                                    kwds[k] = json.dumps(v)
                        else:
                            raise ParameterTypeError(k, types[k])
            ignored = set(types.keys())
            ignored.difference_update(set(kwds.keys()))
            for nonparam in ignored:
                m.warning("specified parameter {0} not in function".format(nonparam))
            return f(*args, **kwds)
        new_f.func_name = f.func_name
        return new_f
    return check_accepts
