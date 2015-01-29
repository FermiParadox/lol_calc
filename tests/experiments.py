from abc import ABCMeta


class BaseClass(metaclass=ABCMeta):

    def d(self):
        return self.D


class InClass(BaseClass):

    D = {1: 2}



inst = InClass()

print(inst.d())
