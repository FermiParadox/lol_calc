import timeit

setup = """
a = 123
b = 12

s = {True, False}
"""

stmt1 = "isinstance(a, bool) ; isinstance(b, bool)"
stmt2 = "isinstance(a, int) ; isinstance(b, int)"

stmt3 = "a is True or a is False; b is True or b is False"

stmt4 = "type(a) is bool; type(b) is bool"
stmt5 = "a.__class__ is bool ; b.__class__ is bool"

stmt6 = "a in s ; b in s"


repetitions = 10**6
t1 = timeit.timeit(stmt1, setup=setup, number=repetitions)
t2 = timeit.timeit(stmt2, setup=setup, number=repetitions)
t3 = timeit.timeit(stmt3, setup=setup, number=repetitions)
t4 = timeit.timeit(stmt4, setup=setup, number=repetitions)
t5 = timeit.timeit(stmt5, setup=setup, number=repetitions)
t6 = timeit.timeit(stmt6, setup=setup, number=repetitions)


print(t1)
print(t2)
print(t3)
print(t4)
print(t5)
print(t6)