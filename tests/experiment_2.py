import timeit

d = {1: 1, 2: 2, 3: 3, 4: 4}



t1 = timeit.timeit('for i in d: i', 'd = {1: 1, 2: 2, 3: 3, 4: 4}')
t2 = timeit.timeit('for i in s: i', """
d = {1: 1, 2: 2, 3: 3, 4: 4}
s = d.keys()""")

print(t1,t2)