S = {'dog': 2}


class ClassA(object):

    def __init__(self, a, d):
        self.a = a
        for i in d:
            setattr(ClassA, i, d[i])

    def f(self):
        return self.a, self.dog

inst = ClassA(a=1, d={'c':4})
print(inst.f())
