class ClassA(object):

    def f(self):
        return 0

    def g(self):
        return self.f() + 10


class ClassB(ClassA):

    def f(self):
        return 2

print(ClassB().g())