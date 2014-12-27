import re

def f(x):
    p=re.compile(r'(?P<name>hi)(?:\wi)')
    s=p.findall('hihhinibiii')
    print(s)



if __name__ == '__main__':

    f(1)