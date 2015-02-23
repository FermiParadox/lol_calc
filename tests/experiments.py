d = {1: 11, 2: 22}

s = '%s and %s' % tuple(d.items())[0]

print(s)
print(tuple(d.items()))