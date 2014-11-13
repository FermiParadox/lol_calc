class ClassA(object):

    def _f(self):

        return 5


class ClassB(ClassA):

    def f(self):
        self._f()
        return 7


if __name__ == '__main__':

    print (ClassB()._f())