import abc


class MyBase(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def cat(self, d):
        pass


class MyClass(MyBase):

    def cat(self, d):
        d.update({1: 2})

s = {1: 11}
MyClass().cat(s)
print(s)
