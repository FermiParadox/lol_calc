import re

p1 = re.compile(r'1')

p2 = re.compile(r'2')

p3 = r'%s' % 'cat'

print(re.findall(p3, 'cat dog'))