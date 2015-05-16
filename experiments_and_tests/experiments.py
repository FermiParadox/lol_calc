class MyClass1(object):

    def func_1(self):
        return self.func_2() * 2


class MyClass6(MyClass1):

    def func_2(self):
        return 10


a = MyClass6().func_1()
print(a)  # Prints 20