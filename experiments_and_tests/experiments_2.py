import abc


class MyClass1(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def func_2(self):
        return 'zzzz'

    def func_1(self):
        return self.func_2() * 2


class MyClass4(MyClass1):
    pass


class MyClass5(MyClass4):

    def func_2(self):
        return 10


a = MyClass5().func_1()
print(a)    # Prints 20