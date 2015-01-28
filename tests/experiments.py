import timeit

setup = """
class MyClass(object):

    D = {'a': {'b': {'c': 2}}}

    B = D['a']['b']

    def b1(self):
        return self.D['a']['b']

    def b2(self):
        return self.B
"""

t1 = timeit.timeit("MyClass().b1()['c']", setup)
t2 = timeit.timeit("MyClass().b2()['c']", setup)

print(t1)
print(t2)