d = {'a': 'aa', 'b': 'bb'}

print('d', id(d))
print('d["a"]', id(d['a']))

c = {}

c.update(d)

print('c', id(c))
print('c["a"]', id(c['a']))


def f():
    return d


f()['a'] = 1

print(d)