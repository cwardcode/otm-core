from copy import deepcopy


class DotDict(dict):
    """
    Dictionary class supporting keys like "a.b.c" for nested dictionaries
    From http://stackoverflow.com/questions/3797957
     - RM added get()
     - MVM added __deepcopy__()

    Supports get() with a dotted key and a default, e.g.
        config.get('fruit.apple.type', 'delicious')
    as well as creating dotted keys when no keys in the path exist yet, e.g.
        config = DotDict({})
        config.fruit.apple.type = 'macoun'
    """
    def __init__(self, value=None):

        if value is None:
            pass
        elif isinstance(value, dict):
            for key in value:
                self.__setitem__(key, value[key])
        else:
            raise TypeError('Expected dict')

    def _ensure_dot_dict(self, target, restOfKey, myKey):
        if not isinstance(target, DotDict):
            raise KeyError('Cannot set "%s" in "%s" (%s)' %
                           (restOfKey, myKey, repr(target)))

    def __setitem__(self, key, value):
        if '.' in key:
            myKey, restOfKey = key.split('.', 1)
            target = self.setdefault(myKey, DotDict())
            self._ensure_dot_dict(target, restOfKey, myKey)
            target[restOfKey] = value
        else:
            if isinstance(value, dict) and not isinstance(value, DotDict):
                value = DotDict(value)
            dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        # An implementation note about the try blocks below.

        # Django 1.11.17 calls `hasattr(a_dotdict_field, 'resolve_expression')`
        # https://bit.ly/2ZWLoWF

        # The Python 3 documentation says that this ends up calling `getattr`
        # and returning False if an `AttributeError` is raised
        # https://docs.python.org/3/library/functions.html#hasattr

        # For dictionaries, `getattr` ends up calling `__getitem__`. Our
        # implementation of `__getitem__` correctly raises KeyError, and we
        # were relying on a bug in Python 2 where any exception raised during a
        # `hasattr` check would result in False. Now that Python 3 explicitly
        # checks for `AttributeError` we need this workaround
        if '.' not in key:
            try:
                return dict.__getitem__(self, key)
            except KeyError as ke:
                raise AttributeError(ke)
        myKey, restOfKey = key.split('.', 1)
        try:
            target = dict.__getitem__(self, myKey)
        except KeyError as ke:
            raise AttributeError(ke)
        self._ensure_dot_dict(target, restOfKey, myKey)
        return target[restOfKey]

    def get(self, key, default=None):
        if '.' not in key:
            return dict.get(self, key, default)
        myKey, restOfKey = key.split('.', 1)
        if myKey not in self:
            return default
        target = dict.__getitem__(self, myKey)
        self._ensure_dot_dict(target, restOfKey, myKey)
        return target.get(restOfKey, default)

    def __contains__(self, key):
        if '.' not in key:
            return dict.__contains__(self, key)
        myKey, restOfKey = key.split('.', 1)
        target = dict.get(self, myKey)
        if not isinstance(target, DotDict):
            return False
        return restOfKey in target

    def setdefault(self, key, default):
        if key not in self:
            self[key] = default
        return self[key]

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__ = d

    def __deepcopy__(self, memo):
        return DotDict(deepcopy(dict(self), memo))

    __setattr__ = __setitem__
    __getattr__ = __getitem__
