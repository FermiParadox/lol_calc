class A(object):

    def __init__(self):
        self._x = 1


class B(A):

    def f(self):
        return self._x