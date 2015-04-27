class A(object):

    def f(self):
        if not (False or self.cat):
            print('hi')

A().f()