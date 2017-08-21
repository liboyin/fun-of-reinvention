# Iteration 9

from functools import wraps
from inspect import signature

def checked(func):
    sig = signature(func)
    ann = func.__annotations__
    @wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        for name, val in bound.arguments.items():
            if name in ann:
                ann[name].check(val)
        return func(*args, **kwargs)
    return wrapper

class Contract:
    # Own the "dot" (Descriptor)
    def __set__(self, instance, value):
        self.check(value)
        instance.__dict__[self.name] = value

    # Python 3.6+
    def __set_name__(self, cls, name):
        self.name = name

    @classmethod
    def check(cls, value):
        pass

class Typed(Contract):
    type = None
    @classmethod
    def check(cls, value):
        assert isinstance(value, cls.type), f'Expected {cls.type}'
        super().check(value)

class Integer(Typed):
    type = int

class String(Typed):
    type = str

class Positive(Contract):
    @classmethod
    def check(cls, value):
        assert value > 0, 'Must be positive'
        super().check(value)

class Nonempty(Contract):
    @classmethod
    def check(cls, value):
        assert len(value) > 0, 'Must be nonempty'
        super().check(value)

class PositiveInteger(Integer, Positive):
    pass

class NonemptyString(String, Nonempty):
    pass

class Base:
    # Python 3.6+
    @classmethod
    def __init_subclass__(cls):
        # Apply checked decorator
        for name, val in cls.__dict__.items():
            if callable(val):
                setattr(cls, name, checked(val))
        # Instantiate the contracts
        for name, val in cls.__annotations__.items():
            contract = val()
            contract.__set_name__(cls, name)
            setattr(cls, name, contract)

    def __init__(self, *args):
        ann = self.__annotations__
        assert len(args) == len(ann), f'Expected {len(ann)} arguments'
        for name, val in zip(ann, args):
            setattr(self, name, val)

    def __repr__(self):
        args = ','.join(repr(getattr(self, name)) for name in self.__annotations__)
        return f'{type(self).__name__}({args})'

class Player(Base):
    name: NonemptyString
    x: Integer
    y: Integer

    def left(self, dx: PositiveInteger):
        self.x -= dx

    def right(self, dx: PositiveInteger):
        self.x += dx

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        Integer.check(value)
        self._x = value
