import abc


class A(metaclass=abc.ABCMeta):

    @abc.abstractproperty
    def x(self):
        pass

    def f(self):
        for i in self.x:
            print(i)


class B(A):

    def __init__(self):
        self.__x = None

    def big_method(self):
        # Quite a bit of code here.
        return [i for i in range(5)]

    @property
    def x(self):
        # When called for the first time, it stores the value and returns it.
        # When called later, the stored value is returned.
        if self.__x:
            pass
        else:
            self.__x = self.big_method()

        return self.__x

inst = B()
inst.f()