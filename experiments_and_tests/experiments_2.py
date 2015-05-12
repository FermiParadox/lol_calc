
# ---------------------------------------
import abc


class A(metaclass=abc.ABCMeta):

    @abc.abstractproperty
    def x(self):
        pass


class B(A):

    def __init__(self):
        self.x = None
        self.f()

    def f(self):
        self.x = 4

print(B().x)