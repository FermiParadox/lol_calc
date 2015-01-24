class Hi(object):
    def __init__(self):
        self.cat = None

    def func(self):
        pass

if __name__ == '__main__':

    import ast
    import pprint as pp

    code = """
class Hi(object):
    def __init__(self):
        self.cat = None

    def func(self):
        pass"""

    tree = ast.parse(code)

    pp.pprint(ast.dump(tree))