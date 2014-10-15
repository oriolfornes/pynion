from ..errors.mtce import BadMultitonIdentifier as BMI


class Singleton(type):
    instance = {}

    def __call__(cls, *args, **kw):
        if not cls in cls.instance:
            cls.instance[cls] = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance[cls]


class Multiton(type):
    instance = {}

    def __call__(cls, *args, **kw):
        try:                   idkey = cls._IDENTIFIER
        except AttributeError: idkey = 'name'
        if kw and idkey in kw: ident = kw[idkey]
        elif len(args) > 0:    ident = args[0]
        else:                  raise BMI([idkey, cls.__name__])

        if not cls in cls.instance:
            cls.instance.setdefault(cls, {})
        if not ident in cls.instance[cls]:
            cls.instance[cls][ident] = super(Multiton, cls).__call__(*args, **kw)
        return cls.instance[cls][ident]
