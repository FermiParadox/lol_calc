class ClassA(object):
    def __init__(self):
        print('A init')


class ClassB(object):
    def __init__(self):
        print('B init')

    def f(self):
        a = ClassA

        class C(a):    
            def __init__(self):
                # Here i get the weak warning.
                # ...       |     .......
                # ...       v     .......
                a.__init__(self)
                print('C init')

        return C

a_class = ClassB().f()
print('hello')
a_class()