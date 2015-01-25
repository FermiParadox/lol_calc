class Hi(object):
    def __init__(self):
        self.cat = None

    def func(self):
        pass

if __name__ == '__main__':

    import ast
    import pprint as pp
    import json

    dct = {'a': 1, 3:3, 2:2, 4:4}

    code = str(dct)

    tree = ast.parse(code)

    pp.pprint(ast.dump(tree))

    if False:
        with open('champions/jax.py', 'w') as opened_file:
            json.dump(dct, opened_file, indent=4, )

    my_dct = dict(
        k1=1,
        k3=3,
        k2=2 )
    print(pp.pformat(my_dct, width=1))