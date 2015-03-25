import abc


class A(metaclass=abc.ABCMeta):

    @abc.abstractproperty
    def A(self):
        pass


class B(A):

    A = {}


B()