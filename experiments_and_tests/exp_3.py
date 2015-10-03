class ClassA(object):

    A = 4


class ClassB(ClassA):
    B = 5


class ClassC(ClassA):
    B = 18


a = ClassB()
print(a.B)


b = ClassC()
print(b.B)